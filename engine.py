"""
SMEPro Orchestrator - Ontology Engine
CIP-to-NAICS mapping and logic template resolution
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

import requests
from azure.cosmos import CosmosClient, PartitionKey

logger = logging.getLogger('smepro-ontology')


@dataclass
class NAICSMapping:
    """NAICS code mapping with professional standards"""
    naics_code: str
    naics_title: str
    mapping_type: str  # primary, secondary, tertiary
    confidence_score: float
    professional_standards: List[Dict]
    regulatory_frameworks: List[str]
    industry_benchmarks: Dict[str, Any]


@dataclass
class LogicTemplate:
    """Logic template for NAICS-grounded synthesis"""
    template_id: str
    naics_code: str
    template_type: str
    template_name: str
    content: Dict[str, Any]
    ai_prompt_template: str
    version: int


class OntologyEngine:
    """
    Ontology Engine for CIP-to-NAICS Decoding Matrix
    
    Responsibilities:
    - Resolve CIP codes to NAICS mappings
    - Retrieve professional standards
    - Load logic templates
    - Inject NAICS context into AI prompts
    """
    
    def __init__(self, cosmos_endpoint: str = None, cosmos_key: str = None):
        self.cosmos_endpoint = cosmos_endpoint
        self.cosmos_key = cosmos_key
        self.client = None
        self.database = None
        self.container = None
        
        # In-memory cache for development
        self._cache = {}
        self._load_default_mappings()
        
        if cosmos_endpoint and cosmos_key:
            self._init_cosmos()
    
    def _init_cosmos(self):
        """Initialize Cosmos DB connection"""
        try:
            self.client = CosmosClient(self.cosmos_endpoint, self.cosmos_key)
            self.database = self.client.get_database_client('smepro-ontology')
            self.container = self.database.get_container_client('cip_naics_mappings')
            logger.info("Cosmos DB connection established")
        except Exception as e:
            logger.warning(f"Could not connect to Cosmos DB: {e}")
            logger.info("Using in-memory mappings")
    
    def _load_default_mappings(self):
        """Load default CIP-to-NAICS mappings"""
        self._cache = {
            '52.0301': {  # Accounting
                'cip_code': '52.0301',
                'cip_title': 'Accounting',
                'lamar_programs': ['ACCT-BBA', 'ACCT-MS'],
                'naics_mappings': [
                    {
                        'naics_code': '541211',
                        'naics_title': 'Offices of Certified Public Accountants',
                        'mapping_type': 'primary',
                        'confidence_score': 0.95,
                        'professional_standards': [
                            {'source': 'AICPA', 'document': 'Code of Professional Conduct'},
                            {'source': 'FASB', 'document': 'Accounting Standards Codification'}
                        ],
                        'regulatory_frameworks': ['GAAP', 'IFRS', 'SOX'],
                        'industry_benchmarks': {
                            'revenue_per_partner': 2500000,
                            'typical_staff_ratio': 5.5
                        }
                    },
                    {
                        'naics_code': '541219',
                        'naics_title': 'Other Accounting Services',
                        'mapping_type': 'primary',
                        'confidence_score': 0.90,
                        'professional_standards': [
                            {'source': 'AICPA', 'document': 'Statements on Standards for Accounting and Review Services'}
                        ],
                        'regulatory_frameworks': ['GAAP'],
                        'industry_benchmarks': {}
                    }
                ],
                'logic_templates': [
                    'financial_ratio_analysis',
                    'audit_procedures',
                    'tax_planning',
                    'forensic_accounting'
                ]
            },
            '52.0201': {  # Business Administration
                'cip_code': '52.0201',
                'cip_title': 'Business Administration, Management and Operations',
                'lamar_programs': ['BUSN-BBA', 'MBA'],
                'naics_mappings': [
                    {
                        'naics_code': '541611',
                        'naics_title': 'Administrative Management and General Management Consulting Services',
                        'mapping_type': 'primary',
                        'confidence_score': 0.92,
                        'professional_standards': [
                            {'source': 'IMC USA', 'document': 'Certified Management Consultant Code of Ethics'}
                        ],
                        'regulatory_frameworks': [],
                        'industry_benchmarks': {
                            'revenue_per_consultant': 185000,
                            'typical_margin': 0.25
                        }
                    },
                    {
                        'naics_code': '551114',
                        'naics_title': 'Corporate, Subsidiary, and Regional Managing Offices',
                        'mapping_type': 'primary',
                        'confidence_score': 0.88,
                        'professional_standards': [],
                        'regulatory_frameworks': ['SOX'],
                        'industry_benchmarks': {}
                    }
                ],
                'logic_templates': [
                    'strategic_planning',
                    'organizational_design',
                    'change_management',
                    'performance_management'
                ]
            },
            '52.0801': {  # Finance
                'cip_code': '52.0801',
                'cip_title': 'Finance and Financial Management Services',
                'lamar_programs': ['FINA-BBA'],
                'naics_mappings': [
                    {
                        'naics_code': '523110',
                        'naics_title': 'Investment Banking and Securities Dealing',
                        'mapping_type': 'primary',
                        'confidence_score': 0.90,
                        'professional_standards': [
                            {'source': 'CFA Institute', 'document': 'Code of Ethics and Standards of Professional Conduct'}
                        ],
                        'regulatory_frameworks': ['SEC', 'FINRA'],
                        'industry_benchmarks': {}
                    },
                    {
                        'naics_code': '523930',
                        'naics_title': 'Investment Advice',
                        'mapping_type': 'primary',
                        'confidence_score': 0.88,
                        'professional_standards': [
                            {'source': 'CFP Board', 'document': 'Standards of Professional Conduct'}
                        ],
                        'regulatory_frameworks': ['SEC', 'state_regulations'],
                        'industry_benchmarks': {}
                    }
                ],
                'logic_templates': [
                    'portfolio_optimization',
                    'valuation_models',
                    'risk_assessment',
                    'financial_planning'
                ]
            },
            '52.1401': {  # Marketing
                'cip_code': '52.1401',
                'cip_title': 'Marketing',
                'lamar_programs': ['MKTG-BBA'],
                'naics_mappings': [
                    {
                        'naics_code': '541613',
                        'naics_title': 'Marketing Consulting Services',
                        'mapping_type': 'primary',
                        'confidence_score': 0.93,
                        'professional_standards': [
                            {'source': 'AMA', 'document': 'Statement of Ethics'}
                        ],
                        'regulatory_frameworks': ['FTC'],
                        'industry_benchmarks': {}
                    },
                    {
                        'naics_code': '541810',
                        'naics_title': 'Advertising Agencies',
                        'mapping_type': 'primary',
                        'confidence_score': 0.85,
                        'professional_standards': [
                            {'source': '4A\'s', 'document': 'Standards of Practice'}
                        ],
                        'regulatory_frameworks': ['FTC', 'FCC'],
                        'industry_benchmarks': {}
                    }
                ],
                'logic_templates': [
                    'market_segmentation',
                    'customer_journey_mapping',
                    'campaign_planning',
                    'brand_positioning'
                ]
            },
            '52.1301': {  # MIS
                'cip_code': '52.1301',
                'cip_title': 'Management Information Systems',
                'lamar_programs': ['MIS-BBA'],
                'naics_mappings': [
                    {
                        'naics_code': '541511',
                        'naics_title': 'Custom Computer Programming Services',
                        'mapping_type': 'primary',
                        'confidence_score': 0.87,
                        'professional_standards': [
                            {'source': 'ACM', 'document': 'Code of Ethics and Professional Conduct'}
                        ],
                        'regulatory_frameworks': [],
                        'industry_benchmarks': {}
                    },
                    {
                        'naics_code': '541512',
                        'naics_title': 'Computer Systems Design Services',
                        'mapping_type': 'primary',
                        'confidence_score': 0.85,
                        'professional_standards': [
                            {'source': 'ISACA', 'document': 'COBIT Framework'}
                        ],
                        'regulatory_frameworks': ['NIST', 'ISO27001'],
                        'industry_benchmarks': {}
                    }
                ],
                'logic_templates': [
                    'system_architecture',
                    'database_design',
                    'business_process_modeling',
                    'it_governance'
                ]
            },
            '52.0205': {  # Operations Management
                'cip_code': '52.0205',
                'cip_title': 'Operations Management',
                'lamar_programs': ['OPMT-BBA'],
                'naics_mappings': [
                    {
                        'naics_code': '541614',
                        'naics_title': 'Process, Physical Distribution, and Logistics Consulting Services',
                        'mapping_type': 'primary',
                        'confidence_score': 0.91,
                        'professional_standards': [
                            {'source': 'APICS', 'document': 'Supply Chain Operations Reference (SCOR)'}
                        ],
                        'regulatory_frameworks': [],
                        'industry_benchmarks': {}
                    },
                    {
                        'naics_code': '493110',
                        'naics_title': 'General Warehousing and Storage',
                        'mapping_type': 'secondary',
                        'confidence_score': 0.75,
                        'professional_standards': [],
                        'regulatory_frameworks': ['OSHA'],
                        'industry_benchmarks': {}
                    }
                ],
                'logic_templates': [
                    'supply_chain_optimization',
                    'inventory_management',
                    'quality_control',
                    'lean_six_sigma'
                ]
            },
            '52.1302': {  # Business Analytics
                'cip_code': '52.1302',
                'cip_title': 'Business Analytics',
                'lamar_programs': ['BANA-BBA', 'BANA-MS'],
                'naics_mappings': [
                    {
                        'naics_code': '541990',
                        'naics_title': 'All Other Professional, Scientific, and Technical Services',
                        'mapping_type': 'primary',
                        'confidence_score': 0.82,
                        'professional_standards': [
                            {'source': 'INFORMS', 'document': 'Analytics Body of Knowledge'}
                        ],
                        'regulatory_frameworks': [],
                        'industry_benchmarks': {}
                    },
                    {
                        'naics_code': '518210',
                        'naics_title': 'Data Processing, Hosting, and Related Services',
                        'mapping_type': 'secondary',
                        'confidence_score': 0.78,
                        'professional_standards': [
                            {'source': 'DAMA', 'document': 'Data Management Body of Knowledge'}
                        ],
                        'regulatory_frameworks': ['GDPR', 'CCPA'],
                        'industry_benchmarks': {}
                    }
                ],
                'logic_templates': [
                    'predictive_modeling',
                    'data_visualization',
                    'statistical_analysis',
                    'machine_learning'
                ]
            }
        }
    
    def resolve_course_mapping(self, course_id: str) -> Dict[str, Any]:
        """
        Resolve course ID to CIP-to-NAICS mapping
        
        Args:
            course_id: Lamar course ID (e.g., 'ACCT-3310')
        
        Returns:
            Complete mapping with NAICS codes and professional standards
        """
        # Extract CIP from course prefix
        cip_code = self._course_to_cip(course_id)
        
        # Try Cosmos DB first
        if self.container:
            try:
                query = "SELECT * FROM c WHERE c.cip_code = @cip"
                parameters = [{'name': '@cip', 'value': cip_code}]
                results = list(self.container.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True
                ))
                
                if results:
                    return results[0]
            except Exception as e:
                logger.warning(f"Cosmos query failed: {e}")
        
        # Fall back to cache
        if cip_code in self._cache:
            return self._cache[cip_code]
        
        # Return default/unknown mapping
        return self._get_unknown_mapping(cip_code)
    
    def _course_to_cip(self, course_id: str) -> str:
        """Map course ID prefix to CIP code"""
        prefix_map = {
            'ACCT': '52.0301',
            'BUSN': '52.0201',
            'FINA': '52.0801',
            'MKTG': '52.1401',
            'MIS': '52.1301',
            'OPMT': '52.0205',
            'BANA': '52.1302',
            'ENTR': '52.0701',
            'INTB': '52.1101',
            'HRM': '52.1001'
        }
        
        # Extract prefix from course ID
        prefix = course_id.split('-')[0] if '-' in course_id else course_id[:4]
        
        return prefix_map.get(prefix, '52.0201')  # Default to Business Admin
    
    def _get_unknown_mapping(self, cip_code: str) -> Dict[str, Any]:
        """Return default mapping for unknown CIP"""
        return {
            'cip_code': cip_code,
            'cip_title': 'Unknown Program',
            'naics_mappings': [
                {
                    'naics_code': '541611',
                    'naics_title': 'Administrative Management and General Management Consulting Services',
                    'mapping_type': 'primary',
                    'confidence_score': 0.50,
                    'professional_standards': [],
                    'regulatory_frameworks': [],
                    'industry_benchmarks': {}
                }
            ],
            'logic_templates': ['general_business_analysis']
        }
    
    def get_logic_template(self, template_id: str) -> Optional[LogicTemplate]:
        """
        Retrieve logic template by ID
        
        Args:
            template_id: Template identifier
        
        Returns:
            LogicTemplate if found, None otherwise
        """
        # Load from file or database
        templates = self._load_logic_templates()
        
        template_data = templates.get(template_id)
        if template_data:
            return LogicTemplate(
                template_id=template_id,
                naics_code=template_data['naics_code'],
                template_type=template_data['template_type'],
                template_name=template_data['template_name'],
                content=template_data['content'],
                ai_prompt_template=template_data['ai_prompt_template'],
                version=template_data.get('version', 1)
            )
        
        return None
    
    def _load_logic_templates(self) -> Dict[str, Any]:
        """Load logic templates from storage"""
        # In production, load from Cosmos DB or file
        # For now, return embedded templates
        
        return {
            'financial_ratio_analysis': {
                'naics_code': '541211',
                'template_type': 'financial_analysis',
                'template_name': 'Financial Ratio Analysis',
                'content': {
                    'liquidity_ratios': ['current_ratio', 'quick_ratio'],
                    'profitability_ratios': ['gross_margin', 'net_margin', 'roe', 'roa'],
                    'leverage_ratios': ['debt_to_equity', 'interest_coverage'],
                    'efficiency_ratios': ['inventory_turnover', 'receivables_turnover']
                },
                'ai_prompt_template': '''
You are a senior financial analyst at a CPA firm (NAICS 541211). 
Analyze the following financial data using professional standards (GAAP).
Provide ratio calculations with industry benchmarks and interpret the results.

Context: {context}
Data: {data}

Required output:
1. Calculate all relevant ratios
2. Compare to industry benchmarks
3. Provide interpretation and recommendations
4. Cite relevant accounting standards
''',
                'version': 1
            },
            'swot_analysis': {
                'naics_code': '541611',
                'template_type': 'strategic_analysis',
                'template_name': 'SWOT Analysis',
                'content': {
                    'dimensions': ['strengths', 'weaknesses', 'opportunities', 'threats'],
                    'framework': '2x2_matrix',
                    'data_sources': ['internal', 'market', 'competitive']
                },
                'ai_prompt_template': '''
You are a management consultant (NAICS 541611) conducting a SWOT analysis.
Analyze the following business situation and provide a comprehensive SWOT matrix.

Subject: {subject}
Industry: {industry}
Additional context: {context}

Required output:
1. Strengths (internal positive factors)
2. Weaknesses (internal negative factors)
3. Opportunities (external positive factors)
4. Threats (external negative factors)
5. Strategic implications and recommendations
''',
                'version': 1
            },
            'supply_chain_risk': {
                'naics_code': '541614',
                'template_type': 'risk_assessment',
                'template_name': 'Supply Chain Risk Assessment',
                'content': {
                    'risk_categories': ['supplier', 'demand', 'operational', 'logistics'],
                    'assessment_scale': '1-5',
                    'mitigation_strategies': ['dual_sourcing', 'inventory_buffering', 'demand_sensing']
                },
                'ai_prompt_template': '''
You are a supply chain risk consultant (NAICS 541614) using APICS SCOR framework.
Conduct a comprehensive risk assessment for the following supply chain scenario.

Scenario: {scenario}
Industry: {industry}
Geographic scope: {geography}

Required output:
1. Risk identification by category
2. Likelihood and impact assessment (1-5 scale)
3. Risk priority matrix
4. Mitigation strategies with implementation roadmap
5. Monitoring KPIs
''',
                'version': 1
            }
        }
    
    def build_ai_context(self, course_id: str, user_role: str, 
                        template_id: str = None) -> Dict[str, Any]:
        """
        Build complete AI context with NAICS grounding
        
        Args:
            course_id: Lamar course ID
            user_role: 'student', 'instructor', or 'admin'
            template_id: Optional logic template to include
        
        Returns:
            Complete context for AI prompt injection
        """
        # Resolve mapping
        mapping = self.resolve_course_mapping(course_id)
        
        # Get primary NAICS
        primary_naics = mapping['naics_mappings'][0] if mapping['naics_mappings'] else None
        
        # Build context
        context = {
            'course_context': {
                'course_id': course_id,
                'cip_code': mapping['cip_code'],
                'cip_title': mapping['cip_title']
            },
            'naics_context': primary_naics,
            'professional_standards': primary_naics.get('professional_standards', []) if primary_naics else [],
            'regulatory_frameworks': primary_naics.get('regulatory_frameworks', []) if primary_naics else [],
            'user_role': user_role
        }
        
        # Add template if specified
        if template_id:
            template = self.get_logic_template(template_id)
            if template:
                context['logic_template'] = {
                    'template_id': template.template_id,
                    'template_name': template.template_name,
                    'template_type': template.template_type,
                    'content': template.content
                }
                context['ai_prompt_template'] = template.ai_prompt_template
        
        return context
    
    def inject_naics_context(self, prompt: str, context: Dict[str, Any]) -> str:
        """
        Inject NAICS context into user prompt
        
        Args:
            prompt: User's original prompt
            context: AI context from build_ai_context
        
        Returns:
            Augmented prompt with NAICS grounding
        """
        naics = context.get('naics_context')
        standards = context.get('professional_standards', [])
        
        # Build persona injection
        persona_parts = []
        
        if naics:
            persona_parts.append(
                f"You are an expert in {naics['naics_title']} (NAICS {naics['naics_code']})."
            )
        
        if standards:
            standards_text = ', '.join([s['document'] for s in standards[:2]])
            persona_parts.append(
                f"Your analysis follows professional standards: {standards_text}."
            )
        
        if context.get('user_role') == 'student':
            persona_parts.append(
                "You are assisting a university student. Provide educational explanations "
                "and guide them through the learning process."
            )
        
        # Combine
        augmented = '\n\n'.join([
            ' '.join(persona_parts),
            f"Course Context: {context['course_context']['cip_title']} (CIP {context['course_context']['cip_code']})",
            '',
            '---',
            'User Request:',
            prompt
        ])
        
        return augmented
    
    def get_related_naics(self, naics_code: str) -> List[Dict[str, Any]]:
        """
        Get related NAICS codes for cross-functional analysis
        
        Args:
            naics_code: Primary NAICS code
        
        Returns:
            List of related NAICS codes with relationship type
        """
        # Define relationships
        relationships = {
            '541211': [  # Accounting
                {'code': '541219', 'relationship': 'adjacent_service', 'description': 'Other accounting services'},
                {'code': '523930', 'relationship': 'complementary', 'description': 'Investment advice'},
                {'code': '541611', 'relationship': 'client_industry', 'description': 'Management consulting clients'}
            ],
            '541611': [  # Management Consulting
                {'code': '541614', 'relationship': 'specialization', 'description': 'Process consulting'},
                {'code': '541613', 'relationship': 'specialization', 'description': 'Marketing consulting'},
                {'code': '541211', 'relationship': 'complementary', 'description': 'Accounting services'}
            ]
        }
        
        return relationships.get(naics_code, [])
    
    def search_mappings(self, query: str) -> List[Dict[str, Any]]:
        """
        Search CIP-to-NAICS mappings
        
        Args:
            query: Search query
        
        Returns:
            List of matching mappings
        """
        results = []
        query_lower = query.lower()
        
        for cip_code, mapping in self._cache.items():
            # Search CIP title
            if query_lower in mapping['cip_title'].lower():
                results.append(mapping)
                continue
            
            # Search NAICS titles
            for naics in mapping.get('naics_mappings', []):
                if query_lower in naics['naics_title'].lower():
                    results.append(mapping)
                    break
        
        return results
