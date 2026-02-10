# WORKFLOWS.md - Execution Logic

## Workflow Rules

### Trigger: FEATURE_REQUEST
```yaml
Description: Architect -> Frontend -> Python Logic -> Review -> Deploy -> Document
Default Chain: A1 -> A2 -> L1 -> Q3 -> I4 -> U4
Variants: complexity=high => A1 -> A5 -> A2 -> L1 -> Q3 -> Q6 -> I4 -> U4; urgency=high => A1 -> A2 -> L1 -> I4 -> U4
Metrics: deployment_time, code_quality, documentation_completeness
```

### Trigger: SECURITY_VULNERABILITY
```yaml
Description: Audit -> Harden -> Troubleshoot -> Incident Respond -> Document -> Chaos Test
Default Chain: Q1 -> Q2 -> O1 -> O2 -> U4 -> Q8
Variants: severity=critical => Q1 -> Q2 -> O2 -> I4 -> U4 -> Q8; scope=wide => Q1 -> Q2 -> O1 -> O2 -> I3 -> U4 -> Q8
Metrics: time_to_remediation, vulnerability_count, system_availability
```

### Trigger: DATA_AI_PIPELINE
```yaml
Description: Data Eng -> ML Eng -> Science -> Quant -> Market -> Vector DB
Default Chain: D4 -> D2 -> D5 -> B2 -> G1 -> D6
Variants: data_scale=large => D4 -> I1 -> D2 -> D5 -> B2 -> G1 -> D6; real_time=true => D4 -> D2 -> D5 -> A6 -> B2 -> G1
Metrics: model_accuracy, pipeline_latency, business_impact
```

### Trigger: LEGACY_REFACTOR
```yaml
Description: Modernize -> Architect -> Rust Forge -> Optimize -> API Doc -> Test
Default Chain: U6 -> A1 -> L4 -> Q6 -> U4 -> Q7
Variants: complexity=high => U6 -> A1 -> A5 -> L4 -> Q6 -> U4 -> Q7; safety=critical => U6 -> A1 -> L4 -> Q3 -> Q6 -> U4 -> Q7
Metrics: code_coverage, performance_gain, technical_debt_reduction
```

### Trigger: CRYPTO_ARB_MEV
```yaml
Description: AI Agent -> Rust Executor -> Risk Check -> Audit -> Deploy -> Quant
Default Chain: D1 -> L4 -> B3 -> Q1 -> I4 -> B2
Variants: risk=high => D1 -> L4 -> B3 -> Q1 -> Q2 -> I4 -> B2; speed=critical => D1 -> L4 -> I4 -> B2
Metrics: execution_speed, profitability, risk_exposure
```

### Trigger: REAL_TIME_SYSTEM
```yaml
Description: Real-time Architect -> Go -> Network -> Performance -> SRE -> Workflow
Default Chain: A6 -> L3 -> I3 -> Q6 -> O5 -> U7
Variants: scale=massive => A6 -> A1 -> L3 -> I3 -> Q6 -> O5 -> U7; latency=ultra_low => A6 -> L4 -> I3 -> Q6 -> O5 -> U7
Metrics: p99_latency, throughput, system_reliability
```

### Trigger: ML_SYSTEM_DEPLOYMENT
```yaml
Description: MLOps -> ML Eng -> Deploy -> SRE -> Test -> Document
Default Chain: D3 -> D2 -> I4 -> O5 -> Q7 -> U4
Variants: model_size=large => D3 -> D2 -> I1 -> I4 -> O5 -> Q7 -> U4; frequency=high => D3 -> D2 -> I4 -> O5 -> Q7 -> U4 -> D5
Metrics: model_serving_latency, update_frequency, model_accuracy
```

### Trigger: GROWTH_EXPERIMENT
```yaml
Description: Growth Hacker -> Frontend -> Data Science -> Content -> Product -> Document
Default Chain: G4 -> A2 -> D5 -> G1 -> B4 -> U4
Variants: experiment_type=acquisition => G4 -> G1 -> A2 -> D5 -> B4 -> U4; experiment_type=retention => G4 -> G3 -> A2 -> D5 -> B4 -> U4
Metrics: conversion_rate, user_retention, experiment_velocity
```

## Conditional Logic

### IF_OUTPUT_CODE
```yaml
Action: Trigger node Q3 (Code Reviewer)
Trigger Nodes: Q3
Additional: Q7 if test_coverage < 80%, Q6 if performance_critical = true
```

### IF_OUTPUT_ERROR
```yaml
Action: Trigger nodes Q4 (Debugger) + O1 (DevOps)
Trigger Nodes: Q4, O1
Additional: Q5 if error_frequency > threshold, O2 if severity = critical
```

### IF_OUTPUT_SCHEMA
```yaml
Action: Trigger nodes O3 (DB Admin) + L7 (SQL Pro)
Trigger Nodes: O3, L7
Additional: O4 if performance_issues = true, Q1 if contains_sensitive_data = true
```

### IF_OUTPUT_SUCCESS
```yaml
Action: Trigger nodes U4 (API Documenter) + G1 (Content Marketer)
Trigger Nodes: U4, G1
Additional: U5 if developer_experience_focus = true, G4 if growth_opportunity = true
```

### IF_PERFORMANCE_CRITICAL
```yaml
Action: Trigger nodes Q6 (Performance Engineer) + A5 (Architect Reviewer)
Trigger Nodes: Q6, A5
Additional: I5 if observability_needed = true, L8 if wasm_relevant = true
```

### IF_SECURITY_SENSITIVE
```yaml
Action: Trigger nodes Q1 (Security Auditor) + Q2 (Security Hardening)
Trigger Nodes: Q1, Q2
Additional: Q8 for chaos_testing, B3 for risk_assessment
```

### IF_USER_FACING
```yaml
Action: Trigger nodes U5 (DX Optimizer) + S2a (UX Architect)
Trigger Nodes: U5, S2a
Additional: S2d for accessibility, G3 for support_preparation
```

## Workflow Rules

### Trigger: AGENT_LOGIC_UPGRADE
```yaml
Description: Synthetic Thinking -> Algorithmic Benchmarking -> Code Review -> Elite Persona Mapping -> Prompt Engineering
Default Chain: H3 -> H2 -> Q3 -> H6 -> U2
```

### Trigger: DEBUG_TRAINING_LOOP
```yaml
Description: Trace/Error Analysis -> Debugger -> Python Refinement -> Troubleshooter -> Documentation
Default Chain: H5 -> Q4 -> L1 -> O1 -> U4
```

## Conditional Logic

### IF_PURE_CODE_INGESTION
```yaml
Action: Route via H1 (Archives) -> D4 (Data Eng) -> Q3 (Reviewer)
Trigger Nodes: H1, D4, Q3
```
