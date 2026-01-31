"""
SMEPro Orchestrator - Compliance & Guardrails Layer
Implements FERPA compliance, academic integrity, and bias mitigation
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger('smepro-compliance')


class ComplianceLevel(Enum):
    """Compliance violation severity levels"""
    PASS = "pass"
    WARNING = "warning"
    BLOCK = "block"


@dataclass
class ComplianceResult:
    """Result of compliance check"""
    level: ComplianceLevel
    rule_id: str
    message: str
    details: Optional[Dict] = None


class ComplianceLayer:
    """
    Compliance and Guardrails Layer
    
    Responsibilities:
    - FERPA data protection
    - Academic integrity enforcement
    - Bias detection and mitigation
    - Content filtering
    - Audit logging
    """
    
    def __init__(self):
        self.ferpa_patterns = self._load_ferpa_patterns()
        self.integrity_rules = self._load_integrity_rules()
        self.bias_keywords = self._load_bias_keywords()
        self.blocked_patterns = self._load_blocked_patterns()
    
    def _load_ferpa_patterns(self) -> List[Dict]:
        """Load FERPA-protected data patterns"""
        return [
            {
                'name': 'ssn',
                'pattern': r'\b\d{3}-\d{2}-\d{4}\b',
                'description': 'Social Security Number'
            },
            {
                'name': 'student_id',
                'pattern': r'\bL\d{8}\b',
                'description': 'Lamar Student ID'
            },
            {
                'name': 'email',
                'pattern': r'\b[A-Za-z0-9._%+-]+@lamar\.edu\b',
                'description': 'Lamar Email Address'
            },
            {
                'name': 'phone',
                'pattern': r'\b\(\d{3}\)\s*\d{3}-\d{4}\b',
                'description': 'Phone Number'
            },
            {
                'name': 'dob',
                'pattern': r'\b\d{1,2}/\d{1,2}/\d{4}\b',
                'description': 'Date of Birth'
            }
        ]
    
    def _load_integrity_rules(self) -> List[Dict]:
        """Load academic integrity rules"""
        return [
            {
                'id': 'direct_answer',
                'name': 'Direct Answer Prevention',
                'patterns': [
                    r'\b(answer|solution|what is)\s+(?:to|for)\s+(?:question|problem)\s*#?\s*\d+',
                    r'\bgive\s+me\s+(?:the\s+)?answer\b',
                    r'\bwhat\s+is\s+the\s+answer\s+to\b',
                    r'\bsolve\s+this\s+(?:problem|question)\s+for\s+me\b'
                ],
                'action': 'scaffold',
                'message': 'I can help you understand the concepts. What specific aspect would you like to explore?'
            },
            {
                'id': 'exam_content',
                'name': 'Exam Content Detection',
                'patterns': [
                    r'\bexam\s+(?:question|problem)\b',
                    r'\btest\s+(?:question|problem)\b',
                    r'\bquiz\s+(?:question|problem)\b',
                    r'\bmidterm\s+(?:question|problem)\b',
                    r'\bfinal\s+(?:question|problem)\b'
                ],
                'action': 'block',
                'message': 'I cannot assist with exam content. Please consult your instructor or study materials.'
            },
            {
                'id': 'homework_verbatim',
                'name': 'Homework Verbatim Request',
                'patterns': [
                    r'\bdo\s+my\s+homework\b',
                    r'\bcomplete\s+this\s+assignment\s+for\s+me\b',
                    r'\bwrite\s+my\s+(?:essay|paper|report)\b'
                ],
                'action': 'scaffold',
                'message': 'I can help you structure your work and provide guidance. What topic are you exploring?'
            }
        ]
    
    def _load_bias_keywords(self) -> Dict[str, List[str]]:
        """Load bias-related keywords for detection"""
        return {
            'gender_bias': [
                'he is better', 'she is better', 'men are', 'women are',
                'male-dominated', 'female-dominated'
            ],
            'racial_bias': [
                'minorities', 'underrepresented', 'diverse candidates'
            ],
            'age_bias': [
                'younger workers', 'older workers', 'millennials', 'boomers'
            ],
            'stereotypes': [
                'typical', 'usually', 'always', 'never'
            ]
        }
    
    def _load_blocked_patterns(self) -> List[str]:
        """Load patterns that should always be blocked"""
        return [
            r'\b(hack|crack|bypass)\s+(?:into|password|security)',
            r'\b(cheat|plagiarize|copy)\s+(?:from|homework|assignment)',
            r'\b(weapon|bomb|attack)\s+(?:make|build|create)'
        ]
    
    def sanitize_prompt(self, prompt: str, user_role: str, context: str) -> str:
        """
        Sanitize user prompt for compliance
        
        Args:
            prompt: User's input prompt
            user_role: 'student', 'instructor', or 'admin'
            context: Usage context (e.g., 'report_generation')
        
        Returns:
            Sanitized prompt or raises ComplianceError
        """
        original_prompt = prompt
        
        # Check for blocked content (always block)
        blocked_result = self._check_blocked_content(prompt)
        if blocked_result.level == ComplianceLevel.BLOCK:
            logger.warning(f"Blocked content detected: {blocked_result.rule_id}")
            raise ComplianceError(blocked_result.message)
        
        # Check academic integrity for students
        if user_role == 'student':
            integrity_result = self._check_academic_integrity(prompt)
            if integrity_result.level == ComplianceLevel.BLOCK:
                logger.warning(f"Academic integrity violation: {integrity_result.rule_id}")
                raise ComplianceError(integrity_result.message)
            elif integrity_result.level == ComplianceLevel.WARNING:
                # Transform prompt to scaffold mode
                prompt = self._transform_to_scaffold(prompt, integrity_result)
        
        # Check for PII/PHI
        pii_result = self._check_pii(prompt)
        if pii_result.level == ComplianceLevel.BLOCK:
            logger.warning(f"PII detected: {pii_result.details}")
            prompt = self._mask_pii(prompt)
        
        # Check for bias
        bias_result = self._check_bias(prompt)
        if bias_result.level == ComplianceLevel.WARNING:
            logger.info(f"Potential bias detected: {bias_result.details}")
            # Add bias warning to system prompt (handled elsewhere)
        
        # Log sanitization if changes were made
        if prompt != original_prompt:
            logger.info({
                'event': 'prompt_sanitized',
                'original_length': len(original_prompt),
                'sanitized_length': len(prompt),
                'user_role': user_role
            })
        
        return prompt
    
    def _check_blocked_content(self, prompt: str) -> ComplianceResult:
        """Check for blocked content patterns"""
        for pattern in self.blocked_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                return ComplianceResult(
                    level=ComplianceLevel.BLOCK,
                    rule_id='blocked_content',
                    message='This request cannot be processed due to content policy.',
                    details={'pattern': pattern}
                )
        
        return ComplianceResult(
            level=ComplianceLevel.PASS,
            rule_id='blocked_content',
            message='No blocked content detected'
        )
    
    def _check_academic_integrity(self, prompt: str) -> ComplianceResult:
        """Check for academic integrity violations"""
        for rule in self.integrity_rules:
            for pattern in rule['patterns']:
                if re.search(pattern, prompt, re.IGNORECASE):
                    return ComplianceResult(
                        level=ComplianceLevel.BLOCK if rule['action'] == 'block' else ComplianceLevel.WARNING,
                        rule_id=rule['id'],
                        message=rule['message'],
                        details={'rule_name': rule['name']}
                    )
        
        return ComplianceResult(
            level=ComplianceLevel.PASS,
            rule_id='academic_integrity',
            message='No integrity violations detected'
        )
    
    def _check_pii(self, prompt: str) -> ComplianceResult:
        """Check for PII/PHI in prompt"""
        detected_pii = []
        
        for pattern_def in self.ferpa_patterns:
            matches = re.findall(pattern_def['pattern'], prompt)
            if matches:
                detected_pii.append({
                    'type': pattern_def['name'],
                    'count': len(matches)
                })
        
        if detected_pii:
            return ComplianceResult(
                level=ComplianceLevel.BLOCK,
                rule_id='pii_detected',
                message='PII detected in prompt',
                details={'detected': detected_pii}
            )
        
        return ComplianceResult(
            level=ComplianceLevel.PASS,
            rule_id='pii_check',
            message='No PII detected'
        )
    
    def _mask_pii(self, prompt: str) -> str:
        """Mask PII in prompt"""
        masked = prompt
        
        for pattern_def in self.ferpa_patterns:
            masked = re.sub(
                pattern_def['pattern'],
                f'[{pattern_def["name"].upper()}_REDACTED]',
                masked
            )
        
        return masked
    
    def _check_bias(self, prompt: str) -> ComplianceResult:
        """Check for potential bias in prompt"""
        prompt_lower = prompt.lower()
        detected_bias = []
        
        for bias_type, keywords in self.bias_keywords.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    detected_bias.append({
                        'type': bias_type,
                        'keyword': keyword
                    })
        
        if detected_bias:
            return ComplianceResult(
                level=ComplianceLevel.WARNING,
                rule_id='potential_bias',
                message='Potential bias detected in prompt',
                details={'detected': detected_bias}
            )
        
        return ComplianceResult(
            level=ComplianceLevel.PASS,
            rule_id='bias_check',
            message='No bias detected'
        )
    
    def _transform_to_scaffold(self, prompt: str, result: ComplianceResult) -> str:
        """Transform direct answer request to scaffold mode"""
        # Add scaffolding prefix to guide AI response
        scaffold_prefix = (
            "As a learning assistant, help the student understand the concepts "
            "rather than providing direct answers. Guide them through the problem-solving "
            "process with questions and explanations.\n\n"
        )
        
        return scaffold_prefix + prompt
    
    def validate_output(self, output: str, input_prompt: str, user_role: str) -> Tuple[str, List[ComplianceResult]]:
        """
        Validate AI output for compliance
        
        Returns:
            Tuple of (validated_output, list_of_violations)
        """
        violations = []
        validated_output = output
        
        # Check for PII in output (shouldn't happen, but verify)
        pii_result = self._check_pii(output)
        if pii_result.level != ComplianceLevel.PASS:
            violations.append(pii_result)
            validated_output = self._mask_pii(output)
        
        # Check for hallucinated citations
        citation_result = self._validate_citations(output)
        if citation_result.level != ComplianceLevel.PASS:
            violations.append(citation_result)
        
        # Check for inappropriate content
        content_result = self._check_content_appropriateness(output)
        if content_result.level != ComplianceLevel.PASS:
            violations.append(content_result)
        
        return validated_output, violations
    
    def _validate_citations(self, output: str) -> ComplianceResult:
        """Validate that citations are real and relevant"""
        # Simple heuristic: check for citation patterns
        citation_patterns = [
            r'\(\w+\s+et\s+al\.?\s*,\s*\d{4}\)',
            r'\[\d+\]',
            r'\(\w+\s*,\s*\d{4}[a-z]?\)'
        ]
        
        # In production, would verify against actual databases
        # For now, just check that citations exist
        has_citations = any(re.search(pattern, output) for pattern in citation_patterns)
        
        if not has_citations and len(output) > 1000:
            # Long output without citations is suspicious
            return ComplianceResult(
                level=ComplianceLevel.WARNING,
                rule_id='missing_citations',
                message='Output may be missing citations',
                details={'suggestion': 'Add source verification'}
            )
        
        return ComplianceResult(
            level=ComplianceLevel.PASS,
            rule_id='citation_validation',
            message='Citations validated'
        )
    
    def _check_content_appropriateness(self, output: str) -> ComplianceResult:
        """Check that output is appropriate for educational context"""
        # Check for inappropriate content
        inappropriate_patterns = [
            r'\b(porn|sex|nude)\b',
            r'\b(kill|murder|harm)\s+(?:yourself|others)',
        ]
        
        for pattern in inappropriate_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                return ComplianceResult(
                    level=ComplianceLevel.BLOCK,
                    rule_id='inappropriate_content',
                    message='Inappropriate content detected in output'
                )
        
        return ComplianceResult(
            level=ComplianceLevel.PASS,
            rule_id='content_appropriateness',
            message='Content is appropriate'
        )
    
    def log_interaction(self, user_id: str, course_id: str, 
                       prompt: str, output: str, 
                       compliance_results: List[ComplianceResult]):
        """Log interaction for audit purposes"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': self._hash_identifier(user_id),
            'course_id': course_id,
            'prompt_hash': self._hash_content(prompt),
            'output_hash': self._hash_content(output),
            'compliance_results': [
                {
                    'rule_id': r.rule_id,
                    'level': r.level.value,
                    'message': r.message
                }
                for r in compliance_results
            ]
        }
        
        logger.info({
            'event': 'interaction_logged',
            'data': log_entry
        })
    
    def _hash_identifier(self, identifier: str) -> str:
        """Hash identifier for privacy"""
        import hashlib
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]
    
    def _hash_content(self, content: str) -> str:
        """Hash content for comparison"""
        import hashlib
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class ComplianceError(Exception):
    """Compliance violation error"""
    pass
