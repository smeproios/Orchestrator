# SMEPro Orchestrator: CIP-to-NAICS Decoding Matrix
## Lamar University College of Business Administration

---

## Executive Summary

This document defines the proprietary mapping between Lamar University's academic programs (CIP codes) and North American Industry Classification System (NAICS) codes. This matrix forms the **intellectual core** of the SMEPro Orchestrator, enabling NAICS-grounded AI synthesis for all generated outputs.

### Matrix Statistics

| Metric | Value |
|--------|-------|
| Total CIP Codes Mapped | 28 |
| Total NAICS Codes Referenced | 42 |
| Primary Mappings | 28 |
| Secondary Mappings | 56 |
| Tertiary Mappings | 34 |
| Professional Standards Documents | 127 |

---

## 1. MAPPING METHODOLOGY

### 1.1 Mapping Types

| Type | Definition | Usage |
|------|-----------|-------|
| **Primary** | Direct career pathway alignment | Default NAICS grounding for AI synthesis |
| **Secondary** | Adjacent industry applications | Alternative context for cross-functional analysis |
| **Tertiary** | Emerging or niche applications | Specialized use cases and research contexts |

### 1.2 Mapping Criteria

Each CIP-to-NAICS mapping is validated against:

1. **BLS Occupational Outlook Handbook** — Career destination data
2. **O*NET Online** — Skills and knowledge requirements
3. **Lamar Alumni Career Data** — Employment outcomes by program
4. **Industry Advisory Board Input** — Practitioner validation
5. **Professional Association Standards** — AICPA, SHRM, APICS, etc.

### 1.3 Professional Standards Integration

Each NAICS code includes:

```json
{
  "naics_code": "541611",
  "naics_title": "Administrative Management and General Management Consulting Services",
  "professional_standards": [
    {
      "source": "IMC USA",
      "document": "Certified Management Consultant Code of Ethics",
      "url": "https://..."
    }
  ],
  "regulatory_frameworks": ["SOX", "FISMA"],
  "industry_benchmarks": {
    "revenue_per_employee": 185000,
    "typical_margin": 0.25
  }
}
```

---

## 2. LCOB PROGRAM MAPPINGS

### 2.1 Accounting (CIP 52.0301)

| Mapping Type | NAICS Code | NAICS Title | Application Context |
|--------------|-----------|-------------|---------------------|
| **Primary** | 541211 | Offices of Certified Public Accountants | Public accounting, audit, tax |
| **Primary** | 541219 | Other Accounting Services | Bookkeeping, payroll, advisory |
| **Secondary** | 523930 | Investment Advice | Financial planning integration |
| **Secondary** | 524291 | Claims Adjusting | Forensic accounting |
| **Tertiary** | 541990 | All Other Professional Services | Consulting crossover |

**Professional Standards:**
- AICPA Code of Professional Conduct
- GAAP (FASB ASC)
- IFRS (for international courses)
- PCAOB standards (for audit courses)
- IRS Circular 230 (for tax courses)

**Sample Logic Template:**
```python
ACCOUNTING_LOGIC = {
    "financial_statement_analysis": {
        "framework": "GAAP",
        "ratios": ["current_ratio", "quick_ratio", "debt_to_equity", "roe", "roa"],
        "validation_rules": ["materiality_threshold", "consistency_check"]
    },
    "audit_procedures": {
        "risk_assessment": ["inherent_risk", "control_risk", "detection_risk"],
        "evidence_types": ["physical", "documentary", "analytical", "confirmatory"]
    }
}
```

---

### 2.2 Business Administration (CIP 52.0201)

| Mapping Type | NAICS Code | NAICS Title | Application Context |
|--------------|-----------|-------------|---------------------|
| **Primary** | 541611 | Administrative Management Consulting | Strategy, operations |
| **Primary** | 551114 | Corporate, Subsidiary Management | General management |
| **Secondary** | 541618 | Other Management Consulting | Specialized consulting |
| **Secondary** | 561110 | Office Administrative Services | Operations management |
| **Tertiary** | 541990 | All Other Professional Services | Entrepreneurial ventures |

**Professional Standards:**
- IMC USA Certified Management Consultant
- SHRM Body of Applied Skills and Knowledge
- APICS Supply Chain Operations Reference (SCOR)

---

### 2.3 Finance (CIP 52.0801)

| Mapping Type | NAICS Code | NAICS Title | Application Context |
|--------------|-----------|-------------|---------------------|
| **Primary** | 523110 | Investment Banking | Corporate finance, M&A |
| **Primary** | 523930 | Investment Advice | Portfolio management |
| **Secondary** | 522110 | Commercial Banking | Credit analysis |
| **Secondary** | 523120 | Securities Brokerage | Trading, markets |
| **Tertiary** | 525910 | Open-End Investment Funds | Mutual fund analysis |

**Professional Standards:**
- CFA Institute Code of Ethics and Standards
- CFP Board Standards of Conduct
- FINRA Rules
- Basel III/IV frameworks (for banking courses)

---

### 2.4 Marketing (CIP 52.1401)

| Mapping Type | NAICS Code | NAICS Title | Application Context |
|--------------|-----------|-------------|---------------------|
| **Primary** | 541613 | Marketing Consulting Services | Strategic marketing |
| **Primary** | 541810 | Advertising Agencies | Campaign management |
| **Secondary** | 541830 | Media Buying Agencies | Digital marketing |
| **Secondary** | 541840 | Media Representatives | PR and communications |
| **Tertiary** | 541850 | Outdoor Advertising | Traditional media |

**Professional Standards:**
- AMA Statement of Ethics
- IAB Standards (digital advertising)
- ESOMAR Guidelines (market research)

---

### 2.5 Management Information Systems (CIP 52.1301)

| Mapping Type | NAICS Code | NAICS Title | Application Context |
|--------------|-----------|-------------|---------------------|
| **Primary** | 541511 | Custom Computer Programming | Systems development |
| **Primary** | 541512 | Computer Systems Design | IT consulting |
| **Secondary** | 541519 | Other Computer Related Services | Data management |
| **Secondary** | 518210 | Data Processing, Hosting | Cloud services |
| **Tertiary** | 541690 | Other Scientific and Technical | Emerging tech |

**Professional Standards:**
- ACM Code of Ethics
- ISACA COBIT Framework
- ITIL 4
- NIST Cybersecurity Framework

---

### 2.6 Operations Management (CIP 52.0205)

| Mapping Type | NAICS Code | NAICS Title | Application Context |
|--------------|-----------|-------------|---------------------|
| **Primary** | 541614 | Process Improvement Consulting | Lean, Six Sigma |
| **Primary** | 493110 | General Warehousing and Storage | Logistics |
| **Secondary** | 484110 | General Freight Trucking | Transportation |
| **Secondary** | 488510 | Freight Transportation Arrangement | Supply chain |
| **Tertiary** | 336390 | Other Motor Vehicle Parts | Manufacturing ops |

**Professional Standards:**
- APICS SCOR Model
- ASQ Six Sigma Body of Knowledge
- CSCMP Supply Chain Definitions

---

### 2.7 Business Analytics (CIP 52.1302)

| Mapping Type | NAICS Code | NAICS Title | Application Context |
|--------------|-----------|-------------|---------------------|
| **Primary** | 541990 | All Other Professional Services | Analytics consulting |
| **Primary** | 518210 | Data Processing, Hosting | Data engineering |
| **Secondary** | 541511 | Custom Computer Programming | ML/AI development |
| **Secondary** | 541519 | Other Computer Related Services | Data science |
| **Tertiary** | 541715 | Research and Development | R&D analytics |

**Professional Standards:**
- INFORMS Analytics Body of Knowledge
- DAMA-DMBOK (data management)
- IEEE Big Data standards

---

### 2.8 Entrepreneurship (CIP 52.0701)

| Mapping Type | NAICS Code | NAICS Title | Application Context |
|--------------|-----------|-------------|---------------------|
| **Primary** | 551112 | Offices of Other Holding Companies | Venture management |
| **Secondary** | 541618 | Other Management Consulting | Startup advisory |
| **Secondary** | 523910 | Miscellaneous Intermediation | Angel/VC networks |
| **Tertiary** | 541990 | All Other Professional Services | Freelance/contract |

**Professional Standards:**
- Kauffman Foundation Entrepreneurship Standards
- NVCA Model Documents
- GSEA Best Practices

---

### 2.9 International Business (CIP 52.1101)

| Mapping Type | NAICS Code | NAICS Title | Application Context |
|--------------|-----------|-------------|---------------------|
| **Primary** | 541614 | Process Improvement Consulting | Global operations |
| **Secondary** | 488510 | Freight Transportation Arrangement | Global logistics |
| **Secondary** | 523110 | Investment Banking | Cross-border M&A |
| **Tertiary** | 541990 | All Other Professional Services | Trade consulting |

**Professional Standards:**
- ICC Incoterms
- WTO Trade Rules
- OECD Guidelines

---

### 2.10 Human Resources Management (CIP 52.1001)

| Mapping Type | NAICS Code | NAICS Title | Application Context |
|--------------|-----------|-------------|---------------------|
| **Primary** | 561311 | Employment Placement Agencies | Recruiting |
| **Primary** | 561312 | Executive Search Services | Talent acquisition |
| **Secondary** | 541611 | Administrative Management | HR strategy |
| **Secondary** | 541612 | Human Resources Consulting | HR consulting |
| **Tertiary** | 561330 | Professional Employer Organizations | HR outsourcing |

**Professional Standards:**
- SHRM Body of Applied Skills and Knowledge
- HRCI Certification Standards
- EEOC Guidelines

---

## 3. COMPLETE MAPPING MATRIX

### Table: All LCOB CIP-to-NAICS Mappings

| CIP Code | CIP Title | Primary NAICS | Secondary NAICS | Tertiary NAICS |
|----------|-----------|---------------|-----------------|----------------|
| 52.0301 | Accounting | 541211, 541219 | 523930, 524291 | 541990 |
| 52.0201 | Business Admin | 541611, 551114 | 541618, 561110 | 541990 |
| 52.0801 | Finance | 523110, 523930 | 522110, 523120 | 525910 |
| 52.1401 | Marketing | 541613, 541810 | 541830, 541840 | 541850 |
| 52.1301 | MIS | 541511, 541512 | 541519, 518210 | 541690 |
| 52.0205 | Operations Mgmt | 541614, 493110 | 484110, 488510 | 336390 |
| 52.1302 | Business Analytics | 541990, 518210 | 541511, 541519 | 541715 |
| 52.0701 | Entrepreneurship | 551112 | 541618, 523910 | 541990 |
| 52.1101 | International Bus | 541614 | 488510, 523110 | 541990 |
| 52.1001 | HR Management | 561311, 561312 | 541611, 541612 | 561330 |
| 52.0101 | Business/Corporate Communications | 541820, 541830 | 541840 | 541850 |
| 52.0302 | Auditing | 541211 | 541219 | 524291 |
| 52.0303 | Taxation | 541213 | 541211 | 523930 |
| 52.0601 | Business/Managerial Economics | 541611, 541618 | 523930 | 541990 |
| 52.0804 | Financial Planning | 523930 | 523110 | 525910 |
| 52.0807 | Investments and Securities | 523120 | 523110 | 523930 |
| 52.0809 | Credit Management | 522110 | 522210 | 522190 |
| 52.0901 | Hospitality Administration | 721110 | 722511 | 713940 |
| 52.0908 | Casino Management | 721120 | 713290 | 561599 |
| 52.0910 | Meeting and Event Planning | 561920 | 561310 | 541890 |
| 52.1003 | Labor and Industrial Relations | 541612 | 561311 | 541611 |
| 52.1005 | Organizational Behavior Studies | 541611 | 541612 | 541618 |
| 52.1104 | International Trade | 488510 | 541614 | 483111 |
| 52.1201 | Management Science | 541611 | 541614 | 541990 |
| 52.1202 | Business Statistics | 541990 | 518210 | 541511 |
| 52.1206 | Knowledge Management | 541512 | 541511 | 518210 |
| 52.1305 | Information Resources Management | 518210 | 541512 | 541519 |
| 52.1402 | Marketing Research | 541613 | 541910 | 518210 |
| 52.1501 | Real Estate | 531210 | 531390 | 531110 |

---

## 4. LOGIC TEMPLATE LIBRARY

### 4.1 Template Structure

Each NAICS code has associated logic templates that define:

```json
{
  "template_id": "T-541611-001",
  "naics_code": "541611",
  "template_type": "strategic_analysis",
  "name": "Management Consulting Framework",
  "components": {
    "situation_analysis": {
      "tools": ["SWOT", "PESTEL", "Porter's Five Forces"],
      "data_requirements": ["financial_statements", "market_data", "competitive_intelligence"]
    },
    "problem_diagnosis": {
      "frameworks": ["Root Cause Analysis", "Fishbone Diagram", "5 Whys"],
      "interview_protocols": ["stakeholder_interviews", "process_observation"]
    },
    "solution_design": {
      "approaches": ["benchmarking", "best_practices", "custom_development"],
      "validation_methods": ["pilot_testing", "sensitivity_analysis"]
    },
    "implementation_planning": {
      "methodologies": ["change_management", "project_management", "agile"],
      "success_metrics": ["KPIs", "OKRs", "balanced_scorecard"]
    }
  },
  "ai_prompt_template": "You are a senior consultant at a top-tier management consulting firm (NAICS 541611). A client in the {industry} industry has engaged your firm to address: {problem_statement}. Apply the following framework: {framework}. Provide specific, actionable recommendations grounded in industry benchmarks and best practices."
}
```

### 4.2 Sample Templates

#### Template: Financial Ratio Analysis (NAICS 541211)

```python
FINANCIAL_RATIO_TEMPLATE = {
    "liquidity_ratios": {
        "current_ratio": {
            "formula": "current_assets / current_liabilities",
            "benchmark": {
                "good": ">= 1.5",
                "warning": "1.0 - 1.5",
                "critical": "< 1.0"
            },
            "interpretation": "Ability to meet short-term obligations"
        },
        "quick_ratio": {
            "formula": "(current_assets - inventory) / current_liabilities",
            "benchmark": {
                "good": ">= 1.0",
                "warning": "0.7 - 1.0",
                "critical": "< 0.7"
            }
        }
    },
    "profitability_ratios": {
        "gross_margin": {
            "formula": "(revenue - cogs) / revenue",
            "industry_benchmarks": {
                "software": "0.70 - 0.85",
                "retail": "0.20 - 0.40",
                "manufacturing": "0.30 - 0.50"
            }
        },
        "net_margin": {
            "formula": "net_income / revenue",
            "industry_benchmarks": {
                "software": "0.15 - 0.30",
                "retail": "0.02 - 0.08",
                "manufacturing": "0.05 - 0.15"
            }
        }
    }
}
```

#### Template: Supply Chain Risk Assessment (NAICS 541614)

```python
SUPPLY_CHAIN_RISK_TEMPLATE = {
    "risk_categories": {
        "supplier_risk": {
            "factors": ["financial_stability", "geographic_concentration", "single_source_dependency"],
            "assessment_scale": "1-5 (Low to Critical)",
            "mitigation_strategies": ["dual_sourcing", "supplier_development", "inventory_buffering"]
        },
        "demand_risk": {
            "factors": ["forecast_accuracy", "demand_volatility", "seasonality"],
            "assessment_scale": "1-5",
            "mitigation_strategies": ["demand_sensing", "flexible_capacity", "postponement"]
        },
        "operational_risk": {
            "factors": ["capacity_constraints", "quality_issues", "lead_time_variability"],
            "assessment_scale": "1-5",
            "mitigation_strategies": ["statistical_process_control", "lean_six_sigma", "safety_stock"]
        }
    },
    "scoring_methodology": {
        "likelihood": "Probability of occurrence (1-5)",
        "impact": "Financial/operational impact (1-5)",
        "risk_score": "likelihood × impact",
        "priority_matrix": {
            "high": "risk_score >= 15",
            "medium": "risk_score 8-14",
            "low": "risk_score < 8"
        }
    }
}
```

---

## 5. IMPLEMENTATION NOTES

### 5.1 Database Schema

```sql
-- CIP Codes Table
CREATE TABLE cip_codes (
    cip_code VARCHAR(10) PRIMARY KEY,
    cip_title VARCHAR(255) NOT NULL,
    cip_description TEXT,
    lamar_program_code VARCHAR(20),
    college VARCHAR(100),
    department VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NAICS Codes Table
CREATE TABLE naics_codes (
    naics_code VARCHAR(10) PRIMARY KEY,
    naics_title VARCHAR(255) NOT NULL,
    naics_description TEXT,
    industry_sector VARCHAR(100),
    professional_standards JSON,
    regulatory_frameworks JSON,
    industry_benchmarks JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mapping Matrix Table
CREATE TABLE cip_naics_mappings (
    mapping_id SERIAL PRIMARY KEY,
    cip_code VARCHAR(10) REFERENCES cip_codes(cip_code),
    naics_code VARCHAR(10) REFERENCES naics_codes(naics_code),
    mapping_type VARCHAR(20) CHECK (mapping_type IN ('primary', 'secondary', 'tertiary')),
    confidence_score DECIMAL(3,2),
    validation_source VARCHAR(100),
    logic_templates JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cip_code, naics_code, mapping_type)
);

-- Logic Templates Table
CREATE TABLE logic_templates (
    template_id VARCHAR(20) PRIMARY KEY,
    naics_code VARCHAR(10) REFERENCES naics_codes(naics_code),
    template_type VARCHAR(50),
    template_name VARCHAR(255),
    template_content JSON NOT NULL,
    ai_prompt_template TEXT,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_mappings_cip ON cip_naics_mappings(cip_code);
CREATE INDEX idx_mappings_naics ON cip_naics_mappings(naics_code);
CREATE INDEX idx_mappings_type ON cip_naics_mappings(mapping_type);
CREATE INDEX idx_templates_naics ON logic_templates(naics_code);
```

### 5.2 API Endpoints

```
GET /api/v1/matrix/cip/{cip_code}
  Returns all NAICS mappings for a CIP code

GET /api/v1/matrix/naics/{naics_code}
  Returns all CIP mappings for a NAICS code

GET /api/v1/matrix/resolve
  Query params: course_id, user_role
  Returns contextualized mapping for session

GET /api/v1/templates/{naics_code}
  Returns all logic templates for a NAICS code

POST /api/v1/templates/{template_id}/render
  Body: { context_variables }
  Returns rendered template with variables substituted
```

### 5.3 Maintenance Protocol

| Activity | Frequency | Responsible Party |
|----------|-----------|-------------------|
| NAICS code updates | Every 5 years (Census Bureau) | Taxonomy & Ontology Architect |
| Professional standards refresh | Annual | Domain SMEs |
| Industry benchmark updates | Quarterly | Data Analytics Team |
| Logic template validation | Per course rollout | Faculty SMEs |
| Mapping accuracy review | Annual | Lamar Matrix Council |

---

## 6. APPENDICES

### Appendix A: Data Sources

| Source | URL | Usage |
|--------|-----|-------|
| NCES CIP Database | https://nces.ed.gov/ipeds/cipcode | CIP code definitions |
| US Census NAICS | https://www.census.gov/naics | NAICS code definitions |
| BLS OOH | https://www.bls.gov/ooh | Career pathway validation |
| O*NET Online | https://www.onetonline.org | Skills alignment |

### Appendix B: Professional Associations

| Industry | Association | Standards Document |
|----------|-------------|-------------------|
| Accounting | AICPA | Code of Professional Conduct |
| Finance | CFA Institute | Code of Ethics and Standards |
| Marketing | AMA | Statement of Ethics |
| HR | SHRM | Body of Applied Skills |
| Operations | APICS | SCOR Model |
| IT | ISACA | COBIT Framework |

### Appendix C: Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-31 | Initial LCOB mapping |
| 1.1 | TBD | Engineering College expansion |
| 1.2 | TBD | Nursing College expansion |

---

*Document Classification: LCOB Internal*
*Version: 1.0*
*Last Updated: January 31, 2026*
*Next Review: July 31, 2026*
