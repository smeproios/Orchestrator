# SMEPro Orchestrator: Technical Specifications
## Version 2.0 - Strategic Scaling Architecture

---

## Document Control

| Attribute | Value |
|-----------|-------|
| Version | 2.0 |
| Date | January 31, 2026 |
| Status | Strategic Blueprint |
| Classification | LCOB Internal |

---

## 1. SYSTEM OVERVIEW

### 1.1 Architecture Philosophy

The SMEPro Orchestrator implements a **High-Fidelity Domain Synthesis** pattern that bridges academic curriculum (CIP codes) with industrial standards (NAICS codes). The system treats every user request as a contextualized synthesis problem requiring:

1. **Identity Resolution**: Who is asking (student/faculty) and in what context (course/program)
2. **Domain Grounding**: What professional standards apply to this academic domain
3. **Compliance Filtering**: What guardrails must be applied (FERPA, academic integrity)
4. **Synthesis Execution**: How to generate high-fidelity output using CoPilot Enterprise
5. **Runtime Delivery**: How to package output as a functional, deployable artifact

### 1.2 Core Components

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SMEPro Orchestrator Stack                        │
├─────────────────────────────────────────────────────────────────────────┤
│  Layer 6: Runtime Delivery                                               │
│  ├── Report Engine (PDF/Word/PPTX generation)                           │
│  ├── App Builder (React + Python deployment)                            │
│  ├── Analysis Hub (Interactive dashboards)                              │
│  ├── Research Synthesizer (Knowledge graphs)                            │
│  └── Data Pipeline (Notebook-style processing)                          │
├─────────────────────────────────────────────────────────────────────────┤
│  Layer 5: Synthesis Engine                                               │
│  ├── Prompt Engineering Service (template injection)                    │
│  ├── CoPilot Enterprise Middleware (API proxy)                          │
│  ├── Response Validation (quality gates)                                │
│  └── Output Structuring (format conversion)                             │
├─────────────────────────────────────────────────────────────────────────┤
│  Layer 4: Compliance & Guardrails                                        │
│  ├── FERPA Data Masking                                                 │
│  ├── Academic Integrity Filter                                          │
│  ├── Bias Detection & Mitigation                                        │
│  └── Audit Logging                                                      │
├─────────────────────────────────────────────────────────────────────────┤
│  Layer 3: Ontology Engine (CIP↔NAICS)                                    │
│  ├── CIP Code Resolver                                                  │
│  ├── NAICS Code Mapper                                                  │
│  ├── Professional Standards Database                                    │
│  └── Logic Template Library                                             │
├─────────────────────────────────────────────────────────────────────────┤
│  Layer 2: Identity & Context                                             │
│  ├── LTI 1.3 Session Handler                                            │
│  ├── Lamar SSO Integration                                              │
│  ├── Course Context Extraction                                          │
│  └── User Role Determination                                            │
├─────────────────────────────────────────────────────────────────────────┤
│  Layer 1: Infrastructure                                                 │
│  ├── Azure Kubernetes Service (AKS)                                     │
│  ├── Azure OpenAI Service                                               │
│  ├── Azure SQL / Cosmos DB                                              │
│  └── Azure Front Door (CDN/Edge)                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. CAPABILITY 1: INDUSTRY REPORT GENERATOR

### 2.1 Functional Specification

**Purpose**: Generate regulatory compliance and technical documentation reports grounded in NAICS professional standards.

**User Stories**:
- As a Business Admin student, I want to generate a GDPR compliance report so I can understand regulatory frameworks
- As a Management student, I want to create an OSHA safety audit template so I can apply industry standards
- As a faculty member, I want to generate syllabus-aligned case study reports so I can provide consistent learning materials

### 2.2 Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Report Generation Pipeline                   │
├─────────────────────────────────────────────────────────────┤
│  Input: User prompt + Course context                         │
│       ↓                                                      │
│  Step 1: Context Extraction                                  │
│  ├── Parse LTI launch context                                │
│  ├── Resolve Course_ID → CIP_Code                            │
│  └── Determine report type (compliance/technical/research)   │
│       ↓                                                      │
│  Step 2: NAICS Grounding                                     │
│  ├── Query CIP→NAICS matrix                                  │
│  ├── Retrieve professional standards                         │
│  └── Load regulatory framework requirements                  │
│       ↓                                                      │
│  Step 3: Prompt Synthesis                                    │
│  ├── Inject "Professional Persona" (NAICS-based)             │
│  ├── Apply report template structure                         │
│  └── Add citation requirements                               │
│       ↓                                                      │
│  Step 4: CoPilot Generation                                  │
│  ├── Send augmented prompt to Azure OpenAI                   │
│  ├── Stream response for real-time preview                   │
│  └── Validate output against guardrails                      │
│       ↓                                                      │
│  Step 5: Document Assembly                                   │
│  ├── Convert markdown to target format (PDF/Word)            │
│  ├── Apply Lamar branding template                           │
│  └── Generate citation bibliography                          │
│       ↓                                                      │
│  Output: Downloadable, professionally formatted report       │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 API Specification

#### Endpoint: `POST /api/v1/reports/generate`

**Request:**
```json
{
  "prompt": "Generate a GDPR compliance report for a mid-sized fintech",
  "course_context": {
    "course_id": "BUSN-4375",
    "cip_code": "52.1301",
    "program": "Management Science"
  },
  "output_format": "pdf",
  "options": {
    "include_executive_summary": true,
    "include_gap_analysis": true,
    "citation_style": "APA"
  }
}
```

**Response:**
```json
{
  "report_id": "rpt-2026-001234",
  "status": "completed",
  "download_url": "/api/v1/reports/download/rpt-2026-001234",
  "metadata": {
    "naics_codes": ["522320", "541611"],
    "regulatory_frameworks": ["GDPR", "CCPA"],
    "generated_at": "2026-01-31T14:32:00Z",
    "word_count": 3450
  }
}
```

### 2.4 Technology Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Frontend | React + TypeScript | Component reusability, type safety |
| PDF Generation | WeasyPrint (Python) | CSS-based styling, academic templates |
| Word Generation | python-docx | Native .docx output for editing |
| Markdown Processing | markdown-it | Intermediate format conversion |
| Citation Management | CSL (Citation Style Language) | APA, MLA, Chicago support |

### 2.5 Report Templates

```python
REPORT_TEMPLATES = {
    "compliance": {
        "sections": [
            "executive_summary",
            "regulatory_framework",
            "applicability_analysis",
            "gap_assessment",
            "recommendations",
            "implementation_roadmap"
        ],
        "default_length": "3000-5000 words"
    },
    "technical": {
        "sections": [
            "abstract",
            "methodology",
            "findings",
            "discussion",
            "conclusion",
            "references"
        ],
        "default_length": "2000-4000 words"
    },
    "case_study": {
        "sections": [
            "introduction",
            "company_background",
            "situation_analysis",
            "solution_framework",
            "results",
            "lessons_learned"
        ],
        "default_length": "1500-3000 words"
    }
}
```

---

## 3. CAPABILITY 2: FULL-STACK APPLICATION BUILDER

### 3.1 Functional Specification

**Purpose**: Generate, build, and deploy functional web applications based on NAICS-grounded business logic.

**User Stories**:
- As an Operations Management student, I want to build a supply chain risk calculator
- As a Finance student, I want to create a portfolio optimization tool
- As a Marketing student, I want to deploy a customer segmentation dashboard

### 3.2 Technical Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Single-Shot Application Builder                       │
├─────────────────────────────────────────────────────────────────────────┤
│  Input: Natural language description of desired application              │
│       ↓                                                                 │
│  Step 1: Intent Classification                                           │
│  ├── Parse application type (calculator/dashboard/form/etc.)            │
│  ├── Extract data inputs and outputs                                     │
│  └── Identify computation requirements                                   │
│       ↓                                                                 │
│  Step 2: Logic Generation                                                │
│  ├── Query NAICS-specific business logic templates                       │
│  ├── Generate Python/JavaScript computation functions                    │
│  └── Validate against professional standards                             │
│       ↓                                                                 │
│  Step 3: UI Component Selection                                          │
│  ├── Map inputs to form components (sliders, dropdowns, etc.)           │
│  ├── Map outputs to visualization components (charts, tables, etc.)     │
│  └── Assemble responsive layout                                          │
│       ↓                                                                 │
│  Step 4: Code Generation                                                 │
│  ├── Generate React frontend components                                  │
│  ├── Generate FastAPI backend endpoints                                  │
│  ├── Generate database schema (if needed)                                │
│  └── Generate Docker configuration                                       │
│       ↓                                                                 │
│  Step 5: Build & Deploy                                                  │
│  ├── Containerize application                                            │
│  ├── Push to Azure Container Registry                                    │
│  ├── Deploy to Azure Container Apps                                      │
│  └── Configure custom subdomain (optional)                               │
│       ↓                                                                 │
│  Output: Live URL + source code repository + deployment pipeline         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Component Library

```typescript
// Pre-built, NAICS-aware UI components
interface ComponentLibrary {
  inputs: {
    CurrencyInput: { currency: string; locale: string };
    PercentageSlider: { min: number; max: number; step: number };
    IndustrySelector: { naics_codes: string[] };
    DateRangePicker: { format: string };
    DataUpload: { accepted_types: string[]; max_size: number };
  };
  visualizations: {
    KPICard: { metric: string; format: string };
    LineChart: { x_axis: string; y_axis: string };
    BarChart: { categories: string[] };
    PieChart: { segments: string[] };
    DataTable: { columns: ColumnDef[] };
    Heatmap: { x_categories: string[]; y_categories: string[] };
  };
  layouts: {
    DashboardLayout: { columns: number };
    CalculatorLayout: { sections: string[] };
    FormLayout: { steps: number };
  };
}
```

### 3.4 API Specification

#### Endpoint: `POST /api/v1/apps/generate`

**Request:**
```json
{
  "prompt": "Build a supply chain risk calculator for automotive suppliers",
  "course_context": {
    "course_id": "OPMT-3310",
    "cip_code": "52.0205",
    "program": "Operations Management"
  },
  "deployment": {
    "custom_domain": false,
    "enable_persistence": true
  }
}
```

**Response:**
```json
{
  "app_id": "app-2026-005678",
  "status": "deployed",
  "url": "https://app-2026-005678.smepro.lamar.edu",
  "repository": "https://github.com/lamar-smepro/app-2026-005678",
  "metadata": {
    "naics_codes": ["336390"],
    "components_used": ["CurrencyInput", "PercentageSlider", "DataTable", "KPICard"],
    "deployed_at": "2026-01-31T14:45:00Z",
    "estimated_monthly_cost": "$12.50"
  }
}
```

### 3.5 Deployment Architecture

```yaml
# Azure Container Apps configuration
apiVersion: 2024-02-02-preview
kind: ContainerApp
metadata:
  name: "{{app_id}}"
spec:
  configuration:
    ingress:
      external: true
      targetPort: 3000
    secrets:
      - name: database-connection
        value: "{{db_connection_string}}"
  template:
    containers:
      - name: frontend
        image: "{{acr_url}}/smepro-frontend:{{version}}"
        resources:
          cpu: 0.5
          memory: 1Gi
      - name: backend
        image: "{{acr_url}}/smepro-backend:{{version}}"
        resources:
          cpu: 0.5
          memory: 1Gi
        env:
          - name: DATABASE_URL
            secretRef: database-connection
    scale:
      minReplicas: 1
      maxReplicas: 5
      rules:
        - name: http-rule
          http:
            metadata:
              concurrentRequests: "100"
```

---

## 4. CAPABILITY 3: STRATEGIC ANALYSIS ENGINE

### 4.1 Functional Specification

**Purpose**: Conduct SWOT, market research, feasibility studies, and other strategic analyses with real-time data integration.

**User Stories**:
- As a Strategic Management student, I want to conduct a competitive analysis of the streaming industry
- As an Entrepreneurship student, I want to evaluate market entry feasibility for a new product
- As a faculty member, I want to generate industry outlook briefs for classroom discussion

### 4.2 Technical Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Strategic Analysis Pipeline                           │
├─────────────────────────────────────────────────────────────────────────┤
│  Input: Analysis type + subject domain + scope parameters                │
│       ↓                                                                 │
│  Step 1: Analysis Type Routing                                           │
│  ├── SWOT Analysis → Internal/External factor framework                  │
│  ├── Market Research → TAM/SAM/SOM sizing                                │
│  ├── Feasibility Study → Technical/Economic/Operational evaluation       │
│  └── Competitive Analysis → Porter's Five Forces + Market mapping        │
│       ↓                                                                 │
│  Step 2: Data Ingestion                                                  │
│  ├── Query financial databases (Yahoo Finance, SEC EDGAR)               │
│  ├── Scrape industry reports (IBISWorld, Statista)                      │
│  ├── Retrieve news sentiment (GDELT, NewsAPI)                           │
│  └── Aggregate social signals (Twitter, Reddit - if applicable)         │
│       ↓                                                                 │
│  Step 3: Synthesis & Analysis                                            │
│  ├── Apply NAICS-specific analytical frameworks                          │
│  ├── Generate insights with CoPilot Enterprise                           │
│  └── Validate against professional standards                             │
│       ↓                                                                 │
│  Step 4: Visualization Generation                                        │
│  ├── Create interactive charts and matrices                              │
│  ├── Generate comparison tables                                          │
│  └── Build scenario models                                               │
│       ↓                                                                 │
│  Output: Interactive dashboard + executive brief + raw data export       │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Analysis Frameworks

```python
ANALYSIS_FRAMEWORKS = {
    "swot": {
        "dimensions": ["strengths", "weaknesses", "opportunities", "threats"],
        "data_sources": ["financial", "market", "competitive", "regulatory"],
        "output_format": "2x2_matrix"
    },
    "porters_five_forces": {
        "dimensions": [
            "threat_of_new_entrants",
            "bargaining_power_of_suppliers",
            "bargaining_power_of_buyers",
            "threat_of_substitutes",
            "competitive_rivalry"
        ],
        "data_sources": ["industry", "financial", "regulatory"],
        "output_format": "radar_chart"
    },
    "market_sizing": {
        "dimensions": ["tam", "sam", "som"],
        "data_sources": ["demographic", "economic", "industry"],
        "output_format": "funnel_chart"
    },
    "feasibility": {
        "dimensions": ["technical", "economic", "operational", "legal"],
        "data_sources": ["technical", "financial", "regulatory"],
        "output_format": "scorecard"
    }
}
```

### 4.4 API Specification

#### Endpoint: `POST /api/v1/analysis/conduct`

**Request:**
```json
{
  "analysis_type": "swot",
  "subject": "Tesla entering the Indian EV market",
  "course_context": {
    "course_id": "MKTG-4320",
    "cip_code": "52.1401",
    "program": "Marketing"
  },
  "parameters": {
    "time_horizon": "5_years",
    "geographic_scope": ["India"],
    "competitors": ["Tata Motors", "Mahindra", "BYD"]
  }
}
```

**Response:**
```json
{
  "analysis_id": "anl-2026-009012",
  "status": "completed",
  "dashboard_url": "/analysis/anl-2026-009012",
  "results": {
    "swot_matrix": {
      "strengths": ["Brand recognition", "Supercharger network", "Battery tech"],
      "weaknesses": ["High price point", "Limited local manufacturing"],
      "opportunities": ["Government EV subsidies", "Growing middle class"],
      "threats": ["Local competition", "Import tariffs"]
    },
    "market_data": {
      "india_ev_market_size_2026": "$5.2B",
      "projected_cagr": "35%",
      "tesla_estimated_market_share": "8-12%"
    }
  }
}
```

---

## 5. CAPABILITY 4: DEEP RESEARCH SYNTHESIZER

### 5.1 Functional Specification

**Purpose**: Synthesize academic and industry research into structured knowledge bases with source validation and gap analysis.

**User Stories**:
- As a graduate student, I want to conduct a literature review on blockchain in healthcare
- As a research assistant, I want to map the evolution of ESG reporting standards
- As a faculty member, I want to identify research gaps in supply chain resilience

### 5.2 Technical Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Deep Research Pipeline                                │
├─────────────────────────────────────────────────────────────────────────┤
│  Input: Research query + scope parameters + quality thresholds           │
│       ↓                                                                 │
│  Step 1: Search Orchestration                                            │
│  ├── Query academic databases (Google Scholar, PubMed, IEEE)            │
│  ├── Query preprint servers (arXiv, SSRN, bioRxiv)                      │
│  ├── Query industry sources (whitepapers, reports)                      │
│  └── Query regulatory/government sources                                 │
│       ↓                                                                 │
│  Step 2: Source Validation                                               │
│  ├── Check peer-review status                                            │
│  ├── Verify citation metrics (h-index, impact factor)                   │
│  ├── Assess recency and relevance                                        │
│  └── Flag potential predatory sources                                    │
│       ↓                                                                 │
│  Step 3: Content Extraction                                              │
│  ├── Download full-text where available                                  │
│  ├── Extract key findings and methodologies                              │
│  ├── Identify entities (authors, institutions, funding)                 │
│  └── Build citation network                                              │
│       ↓                                                                 │
│  Step 4: Synthesis & Summarization                                       │
│  ├── Cluster related research themes                                     │
│  ├── Generate thematic summaries                                         │
│  ├── Identify consensus and contradictions                               │
│  └── Highlight methodological patterns                                   │
│       ↓                                                                 │
│  Step 5: Knowledge Graph Construction                                    │
│  ├── Extract entities and relationships                                  │
│  ├── Build semantic connections                                          │
│  ├── Identify research gaps                                              │
│  └── Suggest future research directions                                  │
│       ↓                                                                 │
│  Output: Searchable knowledge graph + annotated bibliography + gaps      │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Source Hierarchy

```python
SOURCE_HIERARCHY = {
    "tier_1_academic": {
        "sources": ["peer_reviewed_journals", "conference_proceedings"],
        "weight": 1.0,
        "verification": ["doi_resolution", "crossref_validation"]
    },
    "tier_2_preprint": {
        "sources": ["arXiv", "SSRN", "bioRxiv", "medRxiv"],
        "weight": 0.8,
        "verification": ["author_affiliation", "citation_count"]
    },
    "tier_3_industry": {
        "sources": ["consulting_reports", "industry_whitepapers"],
        "weight": 0.6,
        "verification": ["publisher_reputation", "citation_network"]
    },
    "tier_4_government": {
        "sources": ["regulatory_filings", "government_reports"],
        "weight": 0.7,
        "verification": ["official_source_validation"]
    },
    "tier_5_news": {
        "sources": ["trade_publications", "news_outlets"],
        "weight": 0.4,
        "verification": ["source_credibility_score"]
    }
}
```

### 5.4 API Specification

#### Endpoint: `POST /api/v1/research/synthesize`

**Request:**
```json
{
  "query": "blockchain applications in healthcare records management",
  "course_context": {
    "course_id": "HIM-4400",
    "cip_code": "51.0706",
    "program": "Health Information Management"
  },
  "parameters": {
    "time_range": "2019-2026",
    "source_tiers": ["tier_1", "tier_2", "tier_4"],
    "min_citation_count": 10,
    "max_results": 100
  }
}
```

**Response:**
```json
{
  "research_id": "res-2026-015678",
  "status": "completed",
  "knowledge_graph_url": "/research/res-2026-015678/graph",
  "synthesis": {
    "total_sources": 87,
    "tier_breakdown": {
      "tier_1": 42,
      "tier_2": 28,
      "tier_4": 17
    },
    "key_themes": [
      "Interoperability standards",
      "Patient consent management",
      "Data security & privacy",
      "Clinical trial integrity"
    ],
    "research_gaps": [
      "Limited longitudinal studies on patient outcomes",
      "Insufficient standardization across health systems"
    ],
    "citation_network": {
      "most_cited_paper": "Nakamoto et al. (2020) - 234 citations",
      "emerging_themes": ["AI-blockchain integration", "FHIR compliance"]
    }
  }
}
```

---

## 6. CAPABILITY 5: DATA PROCESSING PIPELINE

### 6.1 Functional Specification

**Purpose**: Ingest, clean, analyze, and visualize datasets with automated insight generation and notebook-style interactivity.

**User Stories**:
- As a Business Analytics student, I want to analyze sales data for seasonal patterns
- As a Finance student, I want to build a credit risk scoring model
- As a faculty member, I want to demonstrate statistical concepts with real datasets

### 6.2 Technical Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Data Processing Pipeline                              │
├─────────────────────────────────────────────────────────────────────────┤
│  Input: Dataset (upload or URL) + analysis intent                        │
│       ↓                                                                 │
│  Step 1: Data Ingestion                                                  │
│  ├── Parse file format (CSV, Excel, JSON, Parquet)                      │
│  ├── Infer schema and data types                                         │
│  ├── Detect encoding and delimiter issues                                │
│  └── Validate file size and structure                                    │
│       ↓                                                                 │
│  Step 2: Data Profiling                                                  │
│  ├── Generate statistical summaries                                      │
│  ├── Detect missing values and outliers                                  │
│  ├── Identify data quality issues                                        │
│  └── Suggest cleaning operations                                         │
│       ↓                                                                 │
│  Step 3: Automated Cleaning                                              │
│  ├── Handle missing values (imputation strategies)                       │
│  ├── Remove or flag outliers                                             │
│  ├── Standardize formats and encodings                                   │
│  └── Create data quality report                                          │
│       ↓                                                                 │
│  Step 4: Analysis Recommendation                                         │
│  ├── Detect data types (time series, categorical, numerical)            │
│  ├── Suggest appropriate statistical tests                               │
│  ├── Recommend visualization types                                       │
│  └── Propose ML models (if applicable)                                   │
│       ↓                                                                 │
│  Step 5: Interactive Analysis                                            │
│  ├── Generate notebook-style interface                                   │
│  ├── Pre-populate recommended analyses                                   │
│  ├── Allow custom code execution (Python/R)                             │
│  └── Enable visualization customization                                  │
│       ↓                                                                 │
│  Output: Cleaned dataset + analysis notebook + insight summary           │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.3 Analysis Recommendations

```python
ANALYSIS_RECOMMENDATIONS = {
    "time_series": {
        "detection": "datetime_index OR temporal_column",
        "suggested_analyses": [
            "seasonal_decomposition",
            "trend_analysis",
            "forecasting",
            "anomaly_detection"
        ],
        "visualizations": ["line_chart", "seasonal_plot", "acf_pacf"]
    },
    "cross_sectional": {
        "detection": "no_temporal_index AND numerical_columns > 2",
        "suggested_analyses": [
            "correlation_analysis",
            "regression",
            "clustering",
            "dimensionality_reduction"
        ],
        "visualizations": ["scatter_matrix", "heatmap", "pca_plot"]
    },
    "categorical": {
        "detection": "categorical_columns > 1",
        "suggested_analyses": [
            "frequency_distribution",
            "chi_square_test",
            "association_rules"
        ],
        "visualizations": ["bar_chart", "pie_chart", "mosaic_plot"]
    }
}
```

### 6.4 API Specification

#### Endpoint: `POST /api/v1/data/upload`

**Request:**
```http
POST /api/v1/data/upload
Content-Type: multipart/form-data

file: sales_data_2025.csv
course_context: {"course_id": "BANA-3300", "cip_code": "52.1302"}
```

**Response:**
```json
{
  "dataset_id": "ds-2026-023456",
  "status": "processed",
  "profile": {
    "rows": 15420,
    "columns": 12,
    "data_types": {
      "numeric": 7,
      "categorical": 4,
      "datetime": 1
    },
    "quality_score": 0.87,
    "issues_detected": [
      "3% missing values in 'customer_segment'",
      "12 outliers detected in 'revenue'"
    ]
  },
  "recommended_analyses": [
    "time_series_forecasting",
    "seasonal_decomposition",
    "customer_segmentation"
  ],
  "notebook_url": "/data/ds-2026-023456/notebook"
}
```

---

## 7. SECURITY & COMPLIANCE SPECIFICATIONS

### 7.1 FERPA Compliance

| Requirement | Implementation |
|-------------|----------------|
| Data Minimization | Only course-level metadata extracted; no PII in AI prompts |
| Access Controls | Role-based permissions (student/faculty/admin) |
| Audit Logging | All AI interactions logged with user/session IDs |
| Data Retention | User outputs retained per academic year; then archived |
| Consent Management | Explicit opt-in for AI-generated content storage |

### 7.2 Academic Integrity Guardrails

```python
ACADEMIC_INTEGRITY_RULES = {
    "direct_answer_prevention": {
        "trigger": "assessment_question_in_prompt",
        "action": "redirect_to_pedagogical_scaffolding",
        "message": "I can help you understand the concepts. What specific aspect would you like to explore?"
    },
    "citation_requirement": {
        "trigger": "factual_claim_in_output",
        "action": "require_source_attribution",
        "minimum_sources": 2
    },
    "originality_check": {
        "trigger": "report_or_essay_generation",
        "action": "embed_watermark_and_hash",
        "verification": "blockchain_attestation_optional"
    }
}
```

### 7.3 API Security

- **Authentication**: OAuth 2.0 + Lamar SSO
- **Authorization**: JWT tokens with course-context claims
- **Rate Limiting**: 100 requests/minute per user; 1000 requests/minute per course
- **Input Validation**: JSON Schema validation + SQL injection prevention
- **Output Sanitization**: HTML escaping + DOMPurify for user-generated content

---

## 8. INFRASTRUCTURE SPECIFICATIONS

### 8.1 Azure Resource Architecture

```yaml
# Infrastructure as Code (Bicep/Terraform)
resourceGroup: "rg-smepro-prod"
location: "southcentralus"

resources:
  aks:
    name: "aks-smepro-prod"
    nodeCount: 3
    vmSize: "Standard_D4s_v3"
    
  openai:
    name: "oai-smepro-prod"
    sku: "S0"
    deployments:
      - name: "gpt-4"
        model: "gpt-4"
        version: "0613"
        capacity: 120
      - name: "gpt-35-turbo"
        model: "gpt-35-turbo"
        version: "0613"
        capacity: 240
        
  database:
    sql:
      name: "sql-smepro-prod"
      tier: "GeneralPurpose"
      capacity: 4
    cosmos:
      name: "cosmos-smepro-prod"
      api: "SQL"
      
  storage:
    name: "stsmeproprod"
    tier: "Standard_LRS"
    
  cdn:
    name: "fd-smepro-prod"
    sku: "Premium_AzureFrontDoor"
```

### 8.2 Cost Estimates (Monthly)

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| AKS | 3 nodes, D4s_v3 | $420 |
| Azure OpenAI | GPT-4 + GPT-3.5 | $2,500 |
| Azure SQL | GP_Gen5_4 | $485 |
| Cosmos DB | 1000 RU/s | $585 |
| Storage | 500 GB | $12 |
| Front Door | Premium | $330 |
| **Total** | | **$4,332** |

---

## 9. MONITORING & OBSERVABILITY

### 9.1 Metrics Dashboard

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| API Response Time | < 500ms | > 1000ms |
| AI Generation Time | < 10s | > 30s |
| Error Rate | < 0.1% | > 0.5% |
| Token Usage | Track | > 80% of quota |
| User Satisfaction | > 4.0/5 | < 3.5/5 |

### 9.2 Logging Strategy

```json
{
  "timestamp": "2026-01-31T14:32:00Z",
  "level": "INFO",
  "service": "smepro-orchestrator",
  "trace_id": "abc123",
  "user_context": {
    "user_id": "hash_of_lamar_id",
    "course_id": "BUSN-4375",
    "cip_code": "52.1301",
    "role": "student"
  },
  "request": {
    "capability": "report_generator",
    "prompt_hash": "sha256_hash",
    "output_format": "pdf"
  },
  "response": {
    "status": "success",
    "duration_ms": 8450,
    "tokens_used": 2450
  }
}
```

---

## 10. APPENDICES

### Appendix A: CIP-to-NAICS Mapping Schema

```sql
CREATE TABLE cip_naics_matrix (
    id INT PRIMARY KEY,
    cip_code VARCHAR(10) NOT NULL,
    cip_title VARCHAR(255),
    naics_code VARCHAR(10) NOT NULL,
    naics_title VARCHAR(255),
    mapping_type ENUM('primary', 'secondary', 'tertiary'),
    professional_standards JSON,
    logic_templates JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_cip (cip_code),
    INDEX idx_naics (naics_code)
);
```

### Appendix B: Prompt Templates

```python
PROFESSIONAL_PERSONA_TEMPLATE = """
You are an expert consultant in {naics_title} (NAICS {naics_code}).
Your advice follows professional standards including: {professional_standards}.
You are assisting a student in {cip_title} (CIP {cip_code}) at Lamar University.
Provide guidance that is pedagogically sound and professionally accurate.
Do not provide direct answers to assessment questions.
Always cite sources when making factual claims.
"""
```

### Appendix C: Glossary

| Term | Definition |
|------|------------|
| CIP | Classification of Instructional Programs - US academic program taxonomy |
| NAICS | North American Industry Classification System - Industry standard taxonomy |
| LTI | Learning Tools Interoperability - LMS integration standard |
| Single-Shot | One-prompt application generation without iterative refinement |
| High-Fidelity Domain Synthesis | AI outputs grounded in professional standards |

---

*Document Version: 2.0*
*Last Updated: January 31, 2026*
*Next Review: February 28, 2026*
