# WORKFLOWS.md - Execution Logic

Generated from `knowledge.json` and `resources.json`.

## Workflow Rules

### FEATURE_REQUEST
> Architect -> Frontend -> Python Logic -> Review -> Deploy -> Document

**Chain:** `A1 -> A2 -> L1 -> Q3 -> I4 -> U4`

**Dynamic Variants:**
- **If complexity=high:** `A1 -> A5 -> A2 -> L1 -> Q3 -> Q6 -> I4 -> U4`
- **If urgency=high:** `A1 -> A2 -> L1 -> I4 -> U4`

**Success Metrics:** deployment_time, code_quality, documentation_completeness

### SECURITY_VULNERABILITY
> Audit -> Harden -> Troubleshoot -> Incident Respond -> Document -> Chaos Test

**Chain:** `Q1 -> Q2 -> O1 -> O2 -> U4 -> Q8`

**Dynamic Variants:**
- **If severity=critical:** `Q1 -> Q2 -> O2 -> I4 -> U4 -> Q8`
- **If scope=wide:** `Q1 -> Q2 -> O1 -> O2 -> I3 -> U4 -> Q8`

**Success Metrics:** time_to_remediation, vulnerability_count, system_availability

### DATA_AI_PIPELINE
> Data Eng -> ML Eng -> Science -> Quant -> Market -> Vector DB

**Chain:** `D4 -> D2 -> D5 -> B2 -> G1 -> D6`

**Dynamic Variants:**
- **If data_scale=large:** `D4 -> I1 -> D2 -> D5 -> B2 -> G1 -> D6`
- **If real_time=true:** `D4 -> D2 -> D5 -> A6 -> B2 -> G1`

**Success Metrics:** model_accuracy, pipeline_latency, business_impact

### LEGACY_REFACTOR
> Modernize -> Architect -> Rust Forge -> Optimize -> API Doc -> Test

**Chain:** `U6 -> A1 -> L4 -> Q6 -> U4 -> Q7`

**Dynamic Variants:**
- **If complexity=high:** `U6 -> A1 -> A5 -> L4 -> Q6 -> U4 -> Q7`
- **If safety=critical:** `U6 -> A1 -> L4 -> Q3 -> Q6 -> U4 -> Q7`

**Success Metrics:** code_coverage, performance_gain, technical_debt_reduction

### CRYPTO_ARB_MEV
> AI Agent -> Rust Executor -> Risk Check -> Audit -> Deploy -> Quant

**Chain:** `D1 -> L4 -> B3 -> Q1 -> I4 -> B2`

**Dynamic Variants:**
- **If risk=high:** `D1 -> L4 -> B3 -> Q1 -> Q2 -> I4 -> B2`
- **If speed=critical:** `D1 -> L4 -> I4 -> B2`

**Success Metrics:** execution_speed, profitability, risk_exposure

### REAL_TIME_SYSTEM
> Real-time Architect -> Go -> Network -> Performance -> SRE -> Workflow

**Chain:** `A6 -> L3 -> I3 -> Q6 -> O5 -> U7`

**Dynamic Variants:**
- **If scale=massive:** `A6 -> A1 -> L3 -> I3 -> Q6 -> O5 -> U7`
- **If latency=ultra_low:** `A6 -> L4 -> I3 -> Q6 -> O5 -> U7`

**Success Metrics:** p99_latency, throughput, system_reliability

### ML_SYSTEM_DEPLOYMENT
> MLOps -> ML Eng -> Deploy -> SRE -> Test -> Document

**Chain:** `D3 -> D2 -> I4 -> O5 -> Q7 -> U4`

**Dynamic Variants:**
- **If model_size=large:** `D3 -> D2 -> I1 -> I4 -> O5 -> Q7 -> U4`
- **If frequency=high:** `D3 -> D2 -> I4 -> O5 -> Q7 -> U4 -> D5`

**Success Metrics:** model_serving_latency, update_frequency, model_accuracy

### GROWTH_EXPERIMENT
> Growth Hacker -> Frontend -> Data Science -> Content -> Product -> Document

**Chain:** `G4 -> A2 -> D5 -> G1 -> B4 -> U4`

**Dynamic Variants:**
- **If experiment_type=acquisition:** `G4 -> G1 -> A2 -> D5 -> B4 -> U4`
- **If experiment_type=retention:** `G4 -> G3 -> A2 -> D5 -> B4 -> U4`

**Success Metrics:** conversion_rate, user_retention, experiment_velocity

### AGENT_LOGIC_UPGRADE
> Synthetic Thinking -> Algorithmic Benchmarking -> Code Review -> Elite Persona Mapping -> Prompt Engineering

**Chain:** `H3 -> H2 -> Q3 -> H6 -> U2`

### DEBUG_TRAINING_LOOP
> Trace/Error Analysis -> Debugger -> Python Refinement -> Troubleshooter -> Documentation

**Chain:** `H5 -> Q4 -> L1 -> O1 -> U4`

---

## Conditional Logic

### IF_OUTPUT_CODE
**Action:** Trigger node Q3 (Code Reviewer)
**Trigger Nodes:** `Q3`
**Additional Checks:**
- Q7 if test_coverage < 80%
- Q6 if performance_critical = true

### IF_OUTPUT_ERROR
**Action:** Trigger nodes Q4 (Debugger) + O1 (DevOps)
**Trigger Nodes:** `Q4 + O1`
**Additional Checks:**
- Q5 if error_frequency > threshold
- O2 if severity = critical

### IF_OUTPUT_SCHEMA
**Action:** Trigger nodes O3 (DB Admin) + L7 (SQL Pro)
**Trigger Nodes:** `O3 + L7`
**Additional Checks:**
- O4 if performance_issues = true
- Q1 if contains_sensitive_data = true

### IF_OUTPUT_SUCCESS
**Action:** Trigger nodes U4 (API Documenter) + G1 (Content Marketer)
**Trigger Nodes:** `U4 + G1`
**Additional Checks:**
- U5 if developer_experience_focus = true
- G4 if growth_opportunity = true

### IF_PERFORMANCE_CRITICAL
**Action:** Trigger nodes Q6 (Performance Engineer) + A5 (Architect Reviewer)
**Trigger Nodes:** `Q6 + A5`
**Additional Checks:**
- I5 if observability_needed = true
- L8 if wasm_relevant = true

### IF_SECURITY_SENSITIVE
**Action:** Trigger nodes Q1 (Security Auditor) + Q2 (Security Hardening)
**Trigger Nodes:** `Q1 + Q2`
**Additional Checks:**
- Q8 for chaos_testing
- B3 for risk_assessment

### IF_USER_FACING
**Action:** Trigger nodes U5 (DX Optimizer) + S2a (UX Architect)
**Trigger Nodes:** `U5 + S2a`
**Additional Checks:**
- S2d for accessibility
- G3 for support_preparation

### IF_PURE_CODE_INGESTION
**Action:** Route via H1 (Archives) -> D4 (Data Eng) -> Q3 (Reviewer)
**Trigger Nodes:** `H1 + D4 + Q3`
