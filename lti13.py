"""
SMEPro Orchestrator - LTI 1.3 Authentication Module
Implements IMS Global LTI 1.3 Advantage specification
"""

import json
import jwt
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from functools import wraps
import hashlib
import secrets

from flask import request, jsonify, current_app


@dataclass
class LTIContext:
    """LTI 1.3 launch context"""
    user_id: str
    user_email: str
    user_name: str
    user_role: str  # 'student', 'instructor', 'admin'
    course_id: str
    course_name: str
    context_id: str
    context_label: str
    context_title: str
    launch_presentation_locale: str
    tool_consumer_info_product_family_code: str
    custom_params: Dict[str, str]
    
    @property
    def is_instructor(self) -> bool:
        return self.user_role in ['instructor', 'admin', 'urn:lti:role:ims/lis/Instructor']
    
    @property
    def is_student(self) -> bool:
        return self.user_role in ['student', 'learner', 'urn:lti:role:ims/lis/Learner']


class LTI13Auth:
    """
    LTI 1.3 Authentication Handler
    
    Implements:
    - OIDC Login Initiation
    - Authentication Response
    - JWT Validation
    - NRPS (Names and Role Provisioning Services)
    - AGS (Assignment and Grade Services)
    """
    
    def __init__(self, app=None):
        self.app = app
        self.platform_configs = {}
        self._jwks_cache = {}
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        
        # Load platform configurations
        app.config.setdefault('LTI13_PLATFORMS', {})
        app.config.setdefault('LTI13_PRIVATE_KEY', None)
        app.config.setdefault('LTI13_PUBLIC_KEY', None)
        app.config.setdefault('LTI13_TOOL_URL', 'https://api.smepro.lamar.edu')
        app.config.setdefault('LTI13_LOGIN_URL', '/lti/login')
        app.config.setdefault('LTI13_LAUNCH_URL', '/lti/launch')
        app.config.setdefault('LTI13_JWKS_URL', '/lti/jwks')
        
        self.platform_configs = app.config['LTI13_PLATFORMS']
    
    def register_platform(self, platform_id: str, config: Dict):
        """
        Register an LMS platform (e.g., Blackboard Ultra)
        
        Args:
            platform_id: Unique identifier for the platform
            config: Platform configuration including:
                - issuer
                - client_id
                - auth_login_url
                - auth_token_url
                - auth_jwks_url
                - deployment_ids
        """
        self.platform_configs[platform_id] = config
        current_app.logger.info(f"Registered LTI 1.3 platform: {platform_id}")
    
    def handle_login(self, request_data: Dict) -> Tuple[str, int]:
        """
        Handle OIDC Login Initiation
        
        Step 1 of LTI 1.3 flow: Platform initiates login
        """
        # Required parameters
        iss = request_data.get('iss')  # Platform issuer
        login_hint = request_data.get('login_hint')
        target_link_uri = request_data.get('target_link_uri')
        
        if not all([iss, login_hint]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Find platform configuration
        platform = self._get_platform_by_issuer(iss)
        if not platform:
            return jsonify({'error': 'Unknown platform issuer'}), 400
        
        # Generate state and nonce
        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)
        
        # Store state for validation later
        self._store_state(state, {
            'platform_id': platform['id'],
            'nonce': nonce,
            'target_link_uri': target_link_uri,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Build authentication request
        auth_request = {
            'scope': 'openid',
            'response_type': 'id_token',
            'client_id': platform['client_id'],
            'redirect_uri': current_app.config['LTI13_TOOL_URL'] + current_app.config['LTI13_LAUNCH_URL'],
            'login_hint': login_hint,
            'state': state,
            'response_mode': 'form_post',
            'nonce': nonce,
            'prompt': 'none'
        }
        
        # Add LTI message hint if provided
        if 'lti_message_hint' in request_data:
            auth_request['lti_message_hint'] = request_data['lti_message_hint']
        
        # Return redirect to platform's authorization endpoint
        auth_url = platform['auth_login_url']
        redirect_url = f"{auth_url}?{'&'.join([f'{k}={v}' for k, v in auth_request.items()])}"
        
        return jsonify({
            'redirect_url': redirect_url,
            'state': state
        }), 200
    
    def handle_launch(self, request_data: Dict) -> Tuple[LTIContext, Optional[Dict]]:
        """
        Handle Authentication Response (Launch)
        
        Step 2 of LTI 1.3 flow: Platform returns ID token
        """
        id_token = request_data.get('id_token')
        state = request_data.get('state')
        
        if not id_token:
            raise LTIError("Missing id_token")
        
        if not state:
            raise LTIError("Missing state")
        
        # Validate state
        stored_state = self._get_state(state)
        if not stored_state:
            raise LTIError("Invalid or expired state")
        
        # Get platform configuration
        platform = self.platform_configs.get(stored_state['platform_id'])
        if not platform:
            raise LTIError("Unknown platform")
        
        # Fetch and cache JWKS
        jwks = self._get_jwks(platform['auth_jwks_url'])
        
        # Validate JWT
        try:
            decoded = self._validate_jwt(id_token, jwks, platform)
        except jwt.InvalidTokenError as e:
            raise LTIError(f"Invalid JWT: {str(e)}")
        
        # Validate nonce
        if decoded.get('nonce') != stored_state['nonce']:
            raise LTIError("Invalid nonce")
        
        # Extract LTI claims
        context = self._extract_lti_context(decoded)
        
        # Extract service endpoints (NRPS, AGS)
        services = self._extract_service_endpoints(decoded)
        
        # Clean up state
        self._delete_state(state)
        
        return context, services
    
    def _validate_jwt(self, token: str, jwks: Dict, platform: Dict) -> Dict:
        """Validate JWT signature and claims"""
        
        # Get unverified header to find key ID
        unverified = jwt.decode(token, options={"verify_signature": False})
        kid = jwt.get_unverified_header(token).get('kid')
        
        # Find matching key
        key = None
        for jwk in jwks.get('keys', []):
            if jwk.get('kid') == kid:
                key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
                break
        
        if not key:
            raise LTIError("Unable to find matching JWK")
        
        # Verify token
        decoded = jwt.decode(
            token,
            key=key,
            algorithms=['RS256'],
            audience=platform['client_id'],
            issuer=platform['issuer']
        )
        
        # Validate LTI-specific claims
        if decoded.get('https://purl.imsglobal.org/spec/lti/claim/version') != '1.3.0':
            raise LTIError("Invalid LTI version")
        
        if not decoded.get('https://purl.imsglobal.org/spec/lti/claim/deployment_id'):
            raise LTIError("Missing deployment_id")
        
        # Validate deployment_id
        deployment_id = decoded['https://purl.imsglobal.org/spec/lti/claim/deployment_id']
        if deployment_id not in platform.get('deployment_ids', []):
            raise LTIError("Invalid deployment_id")
        
        return decoded
    
    def _extract_lti_context(self, decoded: Dict) -> LTIContext:
        """Extract LTI context from decoded JWT"""
        
        lti_claim = 'https://purl.imsglobal.org/spec/lti/claim'
        
        # Get roles
        roles = decoded.get(f'{lti_claim}/roles', [])
        user_role = self._determine_user_role(roles)
        
        # Get context (course info)
        context = decoded.get(f'{lti_claim}/context', {})
        
        # Get custom parameters
        custom = decoded.get(f'{lti_claim}/custom', {})
        
        return LTIContext(
            user_id=decoded.get('sub', ''),
            user_email=decoded.get('email', ''),
            user_name=decoded.get('name', ''),
            user_role=user_role,
            course_id=context.get('id', ''),
            course_name=context.get('title', ''),
            context_id=context.get('id', ''),
            context_label=context.get('label', ''),
            context_title=context.get('title', ''),
            launch_presentation_locale=decoded.get('locale', 'en-US'),
            tool_consumer_info_product_family_code=decoded.get(
                f'{lti_claim}/tool_platform', {}
            ).get('product_family_code', ''),
            custom_params=custom
        )
    
    def _extract_service_endpoints(self, decoded: Dict) -> Dict:
        """Extract NRPS and AGS service endpoints"""
        
        services = {}
        lti_claim = 'https://purl.imsglobal.org/spec/lti/claim'
        
        # Names and Role Provisioning Services
        nrps = decoded.get(f'{lti_claim}/namesroleservice', {})
        if nrps:
            services['nrps'] = {
                'context_memberships_url': nrps.get('context_memberships_url'),
                'service_versions': nrps.get('service_versions', [])
            }
        
        # Assignment and Grade Services
        ags = decoded.get(f'{lti_claim}/ags', {})
        if ags:
            services['ags'] = {
                'lineitems': ags.get('lineitems'),
                'lineitem': ags.get('lineitem'),
                'scope': ags.get('scope', [])
            }
        
        return services
    
    def _determine_user_role(self, roles: list) -> str:
        """Determine user role from LTI roles"""
        
        instructor_roles = [
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Instructor',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor',
            'urn:lti:role:ims/lis/Instructor',
            'Instructor'
        ]
        
        admin_roles = [
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Administrator',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator',
            'urn:lti:role:ims/lis/Administrator',
            'Administrator'
        ]
        
        for role in roles:
            if role in admin_roles:
                return 'admin'
            if role in instructor_roles:
                return 'instructor'
        
        return 'student'
    
    def _get_platform_by_issuer(self, issuer: str) -> Optional[Dict]:
        """Find platform configuration by issuer"""
        for platform_id, config in self.platform_configs.items():
            if config.get('issuer') == issuer:
                return {**config, 'id': platform_id}
        return None
    
    def _get_jwks(self, jwks_url: str) -> Dict:
        """Fetch and cache JWKS from platform"""
        
        if jwks_url in self._jwks_cache:
            cache_entry = self._jwks_cache[jwks_url]
            if cache_entry['expires'] > datetime.utcnow():
                return cache_entry['jwks']
        
        response = requests.get(jwks_url, timeout=10)
        response.raise_for_status()
        jwks = response.json()
        
        self._jwks_cache[jwks_url] = {
            'jwks': jwks,
            'expires': datetime.utcnow() + timedelta(hours=1)
        }
        
        return jwks
    
    def _store_state(self, state: str, data: Dict):
        """Store state for validation (use Redis in production)"""
        # TODO: Implement with Redis
        pass
    
    def _get_state(self, state: str) -> Optional[Dict]:
        """Retrieve stored state (use Redis in production)"""
        # TODO: Implement with Redis
        return None
    
    def _delete_state(self, state: str):
        """Delete stored state (use Redis in production)"""
        # TODO: Implement with Redis
        pass
    
    def get_jwks(self) -> Dict:
        """Return tool's public JWKS for platform registration"""
        
        # In production, load from secure storage
        public_key = current_app.config.get('LTI13_PUBLIC_KEY')
        
        if not public_key:
            raise LTIError("Public key not configured")
        
        # Convert PEM to JWK format
        # This is a simplified version - use proper JWK conversion in production
        return {
            'keys': [{
                'kty': 'RSA',
                'use': 'sig',
                'kid': 'smepro-key-1',
                'alg': 'RS256',
                'n': public_key  # Simplified - should be base64url-encoded modulus
            }]
        }


class LTIError(Exception):
    """LTI 1.3 specific error"""
    pass


def require_lti_auth(f):
    """Decorator to require LTI 1.3 authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        lti_context = getattr(request, 'lti_context', None)
        
        if not lti_context:
            return jsonify({'error': 'LTI authentication required'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_instructor(f):
    """Decorator to require instructor role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        lti_context = getattr(request, 'lti_context', None)
        
        if not lti_context:
            return jsonify({'error': 'LTI authentication required'}), 401
        
        if not lti_context.is_instructor:
            return jsonify({'error': 'Instructor role required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
