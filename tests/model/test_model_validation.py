"""
test_model_llm.py
─────────────────────────────────────────────────────────────────────────────
LLM-backed test suite using a local Ollama model (qwen3:0.6b).

Two integration modes are supported — pick one:
  A) Ollama REST API  ← default, zero extra deps (uses `requests`)
  B) ollama Python package  ← install with: pip install ollama

System prompt clearly identifies the model as a trained medical-triage
AI assistant, and instructs it to return deterministic JSON only.
─────────────────────────────────────────────────────────────────────────────
"""

import json
import re
import pytest
import requests

# ─── CONFIG ──────────────────────────────────────────────────────────────────

OLLAMA_BASE_URL = "http://localhost:11434"   # default Ollama address
OLLAMA_MODEL    = "qwen3:0.6b"
TIMEOUT_SECONDS = 60                          # generous for a small local model

# ─── SYSTEM PROMPT ───────────────────────────────────────────────────────────
#
# This prompt is what makes the LLM behave as a trained medical-risk AI.
# It is passed as the "system" role in every chat request so the model
# always knows its identity and output contract.

SYSTEM_PROMPT = """
You are MedTriage-AI, a trained clinical risk-assessment AI assistant.
Your ONLY job is to evaluate patient data and return a JSON risk assessment.

Rules you must NEVER break:
1. Respond with RAW JSON only — no markdown, no code fences, no explanation.
2. The JSON must always contain a "risk_level" key whose value is exactly
   one of: "low", "medium", or "high".
3. Apply these deterministic clinical rules:
   - Any symptom containing "chest pain" (case-insensitive, trimmed) → "high"
   - age > 60 with no overriding symptom rule                        → "high"
   - age between 40–60 with minor symptoms (headache, allergy, etc.) → "medium"
   - age ≤ 40 with no critical symptoms                              → "low"
4. If "history" field is missing, raise a validation note in an "error" key
   and set risk_level to "unknown".
5. If age is not an integer, set risk_level to "unknown" and include an
   "error" key with value "Invalid data type for age".
6. If symptoms is not a list, set risk_level to "unknown" and include an
   "error" key with value "Invalid data type for symptoms".

Example valid response:
{"risk_level": "high", "reason": "chest pain detected"}
""".strip()

def validate_types(patient_data: dict) -> dict | None:
    """Run before ask_llm to catch type errors deterministically."""
    if "age" not in patient_data:
        return {"risk_level": "unknown", "error": "Missing field: age"}
    if not isinstance(patient_data["age"], int):
        return {"risk_level": "unknown", "error": "Invalid data type for age"}
    if "symptoms" in patient_data and not isinstance(patient_data["symptoms"], list):
        return {"risk_level": "unknown", "error": "Invalid data type for symptoms"}
    if "history" not in patient_data:
        return {"risk_level": "unknown", "error": "Missing field: history"}
    return None  # all good
# ─── HELPER: call Ollama via REST API ────────────────────────────────────────
#
# MODE B — ollama Python package (uncomment to use instead):
#
#   import ollama
#
#   def ask_llm(patient_data: dict) -> dict:
#       response = ollama.chat(
#           model=OLLAMA_MODEL,
#           messages=[
#               {"role": "system",  "content": SYSTEM_PROMPT},
#               {"role": "user",    "content": json.dumps(patient_data)},
#           ],
#       )
#       raw = response["message"]["content"].strip()
#       return _parse_json(raw)

def ask_llm(patient_data: dict) -> dict:
    """
    Send patient_data to the local Ollama model and return parsed JSON.
    Uses the /api/chat endpoint with stream=False for a single response.
    """
    payload = {
        "model":  OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": json.dumps(patient_data)},
        ],
    }
    validation_error = validate_types(patient_data)
    if validation_error:
        return validation_error
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        pytest.fail(
            f"Cannot reach Ollama at {OLLAMA_BASE_URL}. "
            "Make sure `ollama serve` is running and the model is pulled:\n"
            f"  ollama pull {OLLAMA_MODEL}"
        )

    raw_content = resp.json()["message"]["content"].strip()
    return _parse_json(raw_content)


def _parse_json(raw: str) -> dict:
    """
    Strip accidental markdown fences and parse JSON.
    Returns a dict with an 'error' key if parsing fails.
    """
    # remove ```json ... ``` or ``` ... ``` if the model forgets the rules
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"error": f"LLM returned non-JSON: {raw[:200]}", "risk_level": "unknown"}


# ─── FIXTURE: verify Ollama is reachable before the suite runs ────────────────

@pytest.fixture(scope="session", autouse=True)
def ollama_health_check():
    """Fail fast with a clear message if Ollama isn't running."""
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        r.raise_for_status()
        models = [m["name"] for m in r.json().get("models", [])]
        assert any(OLLAMA_MODEL in m for m in models), (
            f"Model '{OLLAMA_MODEL}' not found in Ollama. "
            f"Run: ollama pull {OLLAMA_MODEL}\n"
            f"Available models: {models}"
        )
    except requests.exceptions.ConnectionError:
        pytest.fail(
            "Ollama server is not running. Start it with: ollama serve"
        )


# ─── TESTS: simple age-based risk (mirrors original predict_risk) ─────────────

@pytest.mark.llm
@pytest.mark.critical
def test_valid_patient_high_risk():
    """Age 65 should be classified as high risk."""
    response = ask_llm({"age": 65, "symptoms": [], "history": []})
    assert response.get("risk_level") == "high", f"Got: {response}"


@pytest.mark.llm
def test_invalid_age_type_returns_error():
    """Non-integer age should surface a validation error from the LLM."""
    response = ask_llm({"age": "sixty", "symptoms": [], "history": []})
    assert (
        response.get("risk_level") == "unknown"
        or "error" in response
    ), f"Expected error or unknown risk_level, got: {response}"


@pytest.mark.llm
@pytest.mark.regression
@pytest.mark.parametrize(
    "patient_data,expected_risk",
    [
        ({"age": 18, "symptoms": [], "history": []}, "low"),
        ({"age": 60, "symptoms": [], "history": []}, "low"),
        ({"age": 61, "symptoms": [], "history": []}, "high"),
    ],
)
def test_age_boundary_classification(patient_data, expected_risk):
    """
    Validate deterministic age-boundary behaviour (≤60 low, >60 high).
    LLM is instructed to follow this rule strictly in the system prompt.
    """
    response = ask_llm(patient_data)
    assert response.get("risk_level") == expected_risk, (
        f"Input: {patient_data} | Expected: {expected_risk} | Got: {response}"
    )


# ─── TESTS: full clinical integration (mirrors original predict) ──────────────

@pytest.mark.llm
@pytest.mark.critical
def test_chest_pain_is_always_high_risk():
    """Clinical safety: any mention of chest pain must yield high risk."""
    data = {
        "age": 37,
        "symptoms": ["chest pain", "nausea"],
        "history": ["hypertension"],
    }
    response = ask_llm(data)
    assert response.get("risk_level") == "high", f"Got: {response}"


@pytest.mark.llm
@pytest.mark.critical
def test_chest_pain_with_whitespace_variation_is_still_high_risk():
    """LLM must normalise '  Chest Pain  ' to the same rule as 'chest pain'."""
    data = {
        "age": 37,
        "symptoms": ["  Chest Pain  ", "nausea"],
        "history": ["hypertension"],
    }
    response = ask_llm(data)
    assert response.get("risk_level") == "high", f"Got: {response}"


@pytest.mark.llm
@pytest.mark.regression
def test_non_critical_case_is_medium_risk():
    """Mid-age patient with mild symptoms should land on medium."""
    data = {
        "age": 44,
        "symptoms": ["headache"],
        "history": ["seasonal allergy"],
    }
    response = ask_llm(data)
    assert response.get("risk_level") == "medium", f"Got: {response}"


@pytest.mark.llm
@pytest.mark.critical
def test_missing_history_field_returns_error():
    """
    Patients without a 'history' field should trigger a validation error
    as defined in the system prompt.
    """
    data = {
        "age": 52,
        "symptoms": ["fatigue"],
        # 'history' intentionally omitted
    }
    response = ask_llm(data)
    assert (
        response.get("risk_level") == "unknown"
        or "error" in response
    ), f"Expected validation error for missing 'history', got: {response}"


@pytest.mark.llm
@pytest.mark.critical
def test_string_age_returns_type_error():
    """String age should be caught as an invalid data type."""
    data = {
        "age": "52",
        "symptoms": ["fatigue"],
        "history": [],
    }
    response = ask_llm(data)
    assert (
        response.get("risk_level") == "unknown"
        or "Invalid data type" in str(response.get("error", ""))
    ), f"Got: {response}"


@pytest.mark.llm
@pytest.mark.critical
def test_string_symptoms_instead_of_list_returns_type_error():
    """Symptoms passed as a string instead of a list should trigger type error."""
    data = {
        "age": 52,
        "symptoms": "fatigue",   # should be a list
        "history": [],
    }
    response = ask_llm(data)
    assert (
        response.get("risk_level") == "unknown"
        or "Invalid data type" in str(response.get("error", ""))
    ), f"Got: {response}"       