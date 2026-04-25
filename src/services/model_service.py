def predict(patient_data: dict):
    # Schema validation
    required_fields = ["age", "symptoms", "history"]

    for field in required_fields:
        if field not in patient_data:
            raise ValueError("Missing required field")

    if not isinstance(patient_data["age"], int):
        raise TypeError("Invalid data type")

    # Simulated logic
    if "chest pain" in patient_data["symptoms"]:
        return {"risk_level": "high"}
    elif patient_data["age"] > 100:
        return {"risk_level": "low"}
    else:
        return {"risk_level": "medium"}