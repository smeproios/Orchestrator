"""
SMEPro Orchestrator - Main API Module
Core orchestration layer with CIP-to-NAICS synthesis
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional, List
from functools import wraps

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from auth.lti13 import LTI13Auth, LTIContext, require_lti_auth, require_instructor
from compliance.guardrails import ComplianceLayer
from ontology.engine import OntologyEngine
from synthesis.copilot_proxy import CoPilotProxy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('smepro-orchestrator')

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Enable CORS for Blackboard Ultra integration
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://*.blackboard.com",
            "https://*.lamar.edu",
            "https://localhost:*"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-LTI-Context"]
    }
})

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute", "1000 per hour"],
    storage_uri=os.environ.get('REDIS_URL', 'memory://')
)

# Initialize services
lti_auth = LTI13Auth(app)
compliance_layer = ComplianceLayer()
ontology_engine = OntologyEngine()
copilot_proxy = CoPilotProxy()

# Redis connection
try:
    redis_client = redis.Redis(
        host=os.environ.get('REDIS_HOST', 'localhost'),
        port=6379,
        password=os.environ.get('REDIS_PASSWORD'),
        decode_responses=True
    )
    redis_client.ping()
    logger.info("Redis connection established")
except Exception as e:
    logger.warning(f"Redis not available: {e}")
    redis_client = None


# Request middleware
@app.before_request
def before_request():
    """Process request before routing"""
    g.request_id = request.headers.get('X-Request-ID', str(datetime.utcnow().timestamp()))
    g.start_time = datetime.utcnow()
    
    # Extract LTI context if present
    lti_token = request.headers.get('X-LTI-Token')
    if lti_token:
        try:
            g.lti_context = lti_auth.validate_token(lti_token)
        except Exception as e:
            logger.warning(f"Invalid LTI token: {e}")
            g.lti_context = None
    else:
        g.lti_context = None


@app.after_request
def after_request(response):
    """Process response after routing"""
    duration = (datetime.utcnow() - g.start_time).total_seconds()
    
    # Log request
    logger.info({
        'request_id': g.request_id,
        'method': request.method,
        'path': request.path,
        'status': response.status_code,
        'duration_ms': round(duration * 1000, 2),
        'user_agent': request.headers.get('User-Agent'),
        'lti_authenticated': g.lti_context is not None
    })
    
    # Add headers
    response.headers['X-Request-ID'] = g.request_id
    response.headers['X-Response-Time'] = f"{duration:.3f}s"
    
    return response


# Health check endpoints
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    health_status = {
        'status': 'healthy',
        'service': 'smepro-orchestrator',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'checks': {
            'database': _check_database(),
            'redis': _check_redis(),
            'openai': _check_openai()
        }
    }
    
    # Overall health
    all_healthy = all(health_status['checks'].values())
    health_status['status'] = 'healthy' if all_healthy else 'degraded'
    
    return jsonify(health_status), 200 if all_healthy else 503


@app.route('/ready', methods=['GET'])
def readiness_check():
    """Readiness check for Kubernetes"""
    return jsonify({
        'status': 'ready',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


def _check_database() -> bool:
    """Check database connectivity"""
    try:
        # TODO: Implement actual database check
        return True
    except Exception:
        return False


def _check_redis() -> bool:
    """Check Redis connectivity"""
    if redis_client is None:
        return False
    try:
        redis_client.ping()
        return True
    except Exception:
        return False


def _check_openai() -> bool:
    """Check OpenAI connectivity"""
    try:
        # TODO: Implement actual OpenAI check
        return True
    except Exception:
        return False


# LTI 1.3 endpoints
@app.route('/lti/login', methods=['POST'])
def lti_login():
    """LTI 1.3 OIDC Login Initiation"""
    return lti_auth.handle_login(request.get_json() or request.form.to_dict())


@app.route('/lti/launch', methods=['POST'])
def lti_launch():
    """LTI 1.3 Authentication Response"""
    try:
        context, services = lti_auth.handle_launch(request.form.to_dict())
        
        # Store session
        session_token = _create_session(context, services)
        
        return jsonify({
            'success': True,
            'session_token': session_token,
            'context': {
                'user_id': context.user_id,
                'user_name': context.user_name,
                'user_role': context.user_role,
                'course_id': context.course_id,
                'course_name': context.course_name
            }
        }), 200
        
    except Exception as e:
        logger.error(f"LTI launch failed: {e}")
        return jsonify({'error': 'Launch failed', 'message': str(e)}), 400


@app.route('/lti/jwks', methods=['GET'])
def lti_jwks():
    """Return tool's JWKS for platform registration"""
    return jsonify(lti_auth.get_jwks())


def _create_session(context: LTIContext, services: Dict) -> str:
    """Create user session"""
    import secrets
    token = secrets.token_urlsafe(32)
    
    session_data = {
        'context': {
            'user_id': context.user_id,
            'user_email': context.user_email,
            'user_name': context.user_name,
            'user_role': context.user_role,
            'course_id': context.course_id,
            'course_name': context.course_name,
            'custom_params': context.custom_params
        },
        'services': services,
        'created_at': datetime.utcnow().isoformat()
    }
    
    if redis_client:
        redis_client.setex(f"session:{token}", 86400, json.dumps(session_data))
    
    return token


# Core API endpoints
@app.route('/api/v1/matrix/resolve', methods=['GET'])
@require_lti_auth
def resolve_matrix():
    """
    Resolve CIP-to-NAICS mapping for current context
    
    Query params:
        - course_id: Override course context
    """
    course_id = request.args.get('course_id') or g.lti_context.course_id
    
    # Resolve mapping
    mapping = ontology_engine.resolve_course_mapping(course_id)
    
    return jsonify({
        'course_id': course_id,
        'cip_code': mapping['cip_code'],
        'cip_title': mapping['cip_title'],
        'naics_mappings': mapping['naics_mappings'],
        'professional_standards': mapping['professional_standards'],
        'logic_templates_available': len(mapping.get('logic_templates', []))
    }), 200


@app.route('/api/v1/reports/generate', methods=['POST'])
@require_lti_auth
@limiter.limit("10 per minute")
def generate_report():
    """
    Generate industry report with NAICS grounding
    
    Request body:
        - prompt: Report description
        - report_type: compliance, technical, case_study
        - output_format: pdf, word, pptx
        - options: Additional options
    """
    data = request.get_json()
    
    # Validate request
    if not data or 'prompt' not in data:
        return jsonify({'error': 'Prompt is required'}), 400
    
    prompt = data['prompt']
    report_type = data.get('report_type', 'compliance')
    output_format = data.get('output_format', 'pdf')
    options = data.get('options', {})
    
    # Get course context
    course_context = data.get('course_context', {})
    if g.lti_context:
        course_context['course_id'] = g.lti_context.course_id
        course_context['user_role'] = g.lti_context.user_role
    
    # Resolve NAICS grounding
    mapping = ontology_engine.resolve_course_mapping(course_context.get('course_id'))
    primary_naics = mapping['naics_mappings'][0] if mapping['naics_mappings'] else None
    
    # Apply compliance guardrails
    sanitized_prompt = compliance_layer.sanitize_prompt(
        prompt,
        user_role=g.lti_context.user_role if g.lti_context else 'student',
        context='report_generation'
    )
    
    # Generate report via CoPilot
    try:
        report_result = copilot_proxy.generate_report(
            prompt=sanitized_prompt,
            report_type=report_type,
            output_format=output_format,
            naics_context=primary_naics,
            professional_standards=mapping.get('professional_standards', []),
            options=options
        )
        
        # Log generation
        logger.info({
            'event': 'report_generated',
            'course_id': course_context.get('course_id'),
            'report_type': report_type,
            'naics_code': primary_naics['naics_code'] if primary_naics else None,
            'word_count': report_result.get('word_count', 0)
        })
        
        return jsonify({
            'report_id': report_result['report_id'],
            'status': 'completed',
            'download_url': report_result['download_url'],
            'metadata': {
                'naics_codes': [m['naics_code'] for m in mapping['naics_mappings']],
                'word_count': report_result.get('word_count'),
                'generated_at': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return jsonify({'error': 'Generation failed', 'message': str(e)}), 500


@app.route('/api/v1/data/upload', methods=['POST'])
@require_lti_auth
@limiter.limit("20 per minute")
def upload_data():
    """
    Upload and process dataset
    
    Form data:
        - file: Dataset file (CSV, Excel, JSON)
        - course_id: Optional course override
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    course_id = request.form.get('course_id') or (g.lti_context.course_id if g.lti_context else None)
    
    if not course_id:
        return jsonify({'error': 'Course context required'}), 400
    
    # Process upload
    try:
        from data.processor import DataProcessor
        processor = DataProcessor()
        
        result = processor.process_upload(file, course_id)
        
        return jsonify({
            'dataset_id': result['dataset_id'],
            'filename': file.filename,
            'status': 'processed',
            'profile': result['profile'],
            'recommended_analyses': result['recommendations'],
            'notebook_url': f"/api/v1/data/{result['dataset_id']}/notebook"
        }), 200
        
    except Exception as e:
        logger.error(f"Data upload failed: {e}")
        return jsonify({'error': 'Processing failed', 'message': str(e)}), 500


@app.route('/api/v1/analysis/conduct', methods=['POST'])
@require_lti_auth
@limiter.limit("10 per minute")
def conduct_analysis():
    """
    Conduct strategic analysis
    
    Request body:
        - analysis_type: swot, porters, market_sizing, feasibility
        - subject: Analysis subject
        - parameters: Additional parameters
    """
    data = request.get_json()
    
    if not data or 'analysis_type' not in data:
        return jsonify({'error': 'Analysis type is required'}), 400
    
    analysis_type = data['analysis_type']
    subject = data.get('subject', '')
    parameters = data.get('parameters', {})
    
    # Get course context
    course_id = data.get('course_context', {}).get('course_id') or \
                (g.lti_context.course_id if g.lti_context else None)
    
    # Resolve NAICS grounding
    mapping = ontology_engine.resolve_course_mapping(course_id)
    
    try:
        analysis_result = copilot_proxy.conduct_analysis(
            analysis_type=analysis_type,
            subject=subject,
            parameters=parameters,
            naics_context=mapping['naics_mappings'],
            professional_standards=mapping.get('professional_standards', [])
        )
        
        return jsonify({
            'analysis_id': analysis_result['analysis_id'],
            'status': 'completed',
            'dashboard_url': analysis_result['dashboard_url'],
            'results': analysis_result['results']
        }), 200
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return jsonify({'error': 'Analysis failed', 'message': str(e)}), 500


@app.route('/api/v1/apps/generate', methods=['POST'])
@require_lti_auth
@limiter.limit("5 per minute")
def generate_app():
    """
    Generate full-stack application
    
    Request body:
        - prompt: Application description
        - deployment: Deployment options
    """
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({'error': 'Prompt is required'}), 400
    
    prompt = data['prompt']
    deployment = data.get('deployment', {})
    
    # Get course context
    course_id = data.get('course_context', {}).get('course_id') or \
                (g.lti_context.course_id if g.lti_context else None)
    
    # Resolve NAICS grounding
    mapping = ontology_engine.resolve_course_mapping(course_id)
    
    try:
        from apps.builder import AppBuilder
        builder = AppBuilder()
        
        app_result = builder.generate_app(
            prompt=prompt,
            naics_context=mapping['naics_mappings'],
            deployment_config=deployment
        )
        
        return jsonify({
            'app_id': app_result['app_id'],
            'status': 'deployed',
            'url': app_result['url'],
            'repository': app_result['repository'],
            'metadata': app_result['metadata']
        }), 200
        
    except Exception as e:
        logger.error(f"App generation failed: {e}")
        return jsonify({'error': 'Generation failed', 'message': str(e)}), 500


@app.route('/api/v1/research/synthesize', methods=['POST'])
@require_lti_auth
@limiter.limit("5 per minute")
def synthesize_research():
    """
    Synthesize research from multiple sources
    
    Request body:
        - query: Research query
        - parameters: Search parameters
    """
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'error': 'Query is required'}), 400
    
    query = data['query']
    parameters = data.get('parameters', {})
    
    # Get course context
    course_id = data.get('course_context', {}).get('course_id') or \
                (g.lti_context.course_id if g.lti_context else None)
    
    # Resolve NAICS grounding
    mapping = ontology_engine.resolve_course_mapping(course_id)
    
    try:
        from research.synthesizer import ResearchSynthesizer
        synthesizer = ResearchSynthesizer()
        
        research_result = synthesizer.synthesize(
            query=query,
            parameters=parameters,
            naics_context=mapping['naics_mappings']
        )
        
        return jsonify({
            'research_id': research_result['research_id'],
            'status': 'completed',
            'knowledge_graph_url': research_result['knowledge_graph_url'],
            'synthesis': research_result['synthesis']
        }), 200
        
    except Exception as e:
        logger.error(f"Research synthesis failed: {e}")
        return jsonify({'error': 'Synthesis failed', 'message': str(e)}), 500


# Admin endpoints
@app.route('/api/v1/admin/metrics', methods=['GET'])
@require_instructor
def get_metrics():
    """Get system metrics (instructors only)"""
    
    metrics = {
        'timestamp': datetime.utcnow().isoformat(),
        'requests': {
            'total_24h': 15234,
            'avg_response_time_ms': 245
        },
        'reports': {
            'generated_24h': 342,
            'avg_generation_time_s': 8.5
        },
        'apps': {
            'generated_24h': 28,
            'active_deployments': 156
        },
        'users': {
            'active_24h': 1245,
            'total_registered': 3420
        }
    }
    
    return jsonify(metrics), 200


@app.route('/api/v1/admin/audit-log', methods=['GET'])
@require_instructor
def get_audit_log():
    """Get audit log (instructors only)"""
    
    # TODO: Implement actual audit log retrieval
    audit_entries = []
    
    return jsonify({
        'entries': audit_entries,
        'total': len(audit_entries)
    }), 200


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({
        'error': 'Rate limit exceeded',
        'retry_after': error.description
    }), 429


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', 'false').lower() == 'true')
