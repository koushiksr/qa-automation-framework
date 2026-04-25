# Autonomize AI QA Assignment Test Plan

## Scope

This test plan focuses on:
- Agent integration for healthcare data extraction accuracy and schema compliance.
- Model integration for clinically safe input/output handling.
- UX/UI validation for upload safety guardrails and message clarity.

## Prioritization Matrix

| Priority | Area | Rationale |
|---|---|---|
| P0 (Critical) | Agent schema/type validation | Corrupted extracted data can create patient safety risk. |
| P0 (Critical) | Model high-risk symptom routing | Missed high-risk triage (e.g., chest pain) can cause harm. |
| P1 (High) | Required-field / type error handling | Prevents unsafe model inference from incomplete payloads. |
| P1 (High) | UI invalid format / page-size controls | Prevents unsupported chart uploads and operational failures. |
| P2 (Medium) | Boundary and regression behavior | Maintains deterministic behavior across releases. |

## Implemented Automated Coverage (Pytest)

### 1) Agent Integration (Data Extraction)
- File: `tests/agent/test_agent_flow.py`
- Cases:
  - Valid extracted payload passes schema contract.
  - Invalid age type is rejected.
  - Out-of-range age is rejected.
  - Invalid symptom element types are rejected.

### 2) Model Integration (Input/Output Validation)
- File: `tests/model/test_model_validation.py`
- Cases:
  - Valid high-risk classification by age.
  - Invalid age type returns validation error.
  - Boundary validation at 60/61 for deterministic behavior.
  - Chest pain maps to high risk.
  - Missing required field raises exception.
  - Invalid schema type raises exception.

### 3) UX/UI Validation (User Error Scenario)
- File: `tests/ui/test_ui_validation.py`
- Cases:
  - Invalid chart format rejected with clear message.
  - Excessive file size rejected with clear message.
  - Excessive page count rejected with clear message.
  - Valid upload accepted.

## Example Step-by-Step Test Case (Critical)

### TC-P0-AGENT-001: Reject non-integer patient age from extraction source
1. Simulate extraction output from upstream source with `age` as string.
2. Apply extraction schema validation.
3. Capture validation errors.

Expected:
- Validation fails.
- Error contains `invalid type for age`.

Pass Criteria:
- Unsafe payload is blocked before model consumption.

Fail Criteria:
- Payload accepted despite invalid `age` datatype.

## Regression Recommendations

- Add contract testing against real source payloads (portal/fax/claims).
- Add PII masking tests for logs/reports/artifacts.
- Add negative tests for prompt-injection-like symptom text.
- Add API timeout/retry and partial-outage resiliency tests.
- Add CI pipeline stage gates:
  - P0 failures block merge.
  - P1 failures require approval.

