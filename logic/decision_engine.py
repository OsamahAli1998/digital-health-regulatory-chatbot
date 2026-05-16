def evaluate_regulations(answers):
    """
    Takes user answers and returns possible applicable regulations.
    answers is a dictionary with question ids as keys and True/False as values.
    """

    triggered = []

    if answers.get("personal_data") == True or answers.get("health_data") == True:
        triggered.append("GDPR")

    if answers.get("medical_purpose"):
        triggered.append("MDR")

    if answers.get("swedish_healthcare"):
        triggered.append("HSL")

    if answers.get("patient_records"):
        triggered.append("Patientdatalagen")
        triggered.append("OSL")

    if answers.get("patient_safety"):
        triggered.append("Patientsäkerhetslagen")

    if answers.get("ai_decision"):
        triggered.append("AI_ACT")

    return list(dict.fromkeys(triggered))