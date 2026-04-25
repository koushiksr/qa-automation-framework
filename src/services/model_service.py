def predict(patient_data: dict):
    # Schema validation
    required_fields = ["age", "symptoms", "history"]

    for field in required_fields:
        if field not in patient_data:
            raise ValueError("Missing required field")

    if not isinstance(patient_data["age"], int):
        raise TypeError("Invalid data type")
    if not isinstance(patient_data["symptoms"], list):
        raise TypeError("Invalid data type")
    if not isinstance(patient_data["history"], list):
        raise TypeError("Invalid data type")
    if any(not isinstance(symptom, str) for symptom in patient_data["symptoms"]):
        raise TypeError("Invalid data type")

    # Deterministic triage rules
    normalized_symptoms = {s.strip().lower() for s in patient_data["symptoms"]}
    if "chest pain" in normalized_symptoms:
        return {"risk_level": "high"}
    elif patient_data["age"] > 100:
        return {"risk_level": "low"}
    else:
        return {"risk_level": "medium"}