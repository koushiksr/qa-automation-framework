def predict_risk(patient_data: dict):
    """
    Simulated AI model response
    """

    if not isinstance(patient_data.get("age"), int):
        return {"error": "validation error: age must be integer"}

    if patient_data.get("age") > 60:
        return {"risk": "high"}

    return {"risk": "low"}