# test_chatbot.py
import json
from logic.decision_engine import evaluate_regulations


with open("data/questions.json", "r") as f:
    questions = json.load(f)

# test cases
test_cases = [
    {
        "id": "T1",
        "answers": {
            "personal_data": True,
            "health_data": False,
            "medical_purpose": False,
            "swedish_healthcare": False,
            "patient_records": False,
            "patient_safety": False,
            "ai_decision": False
        },
        "expected": ["GDPR"]
    },
    {
        "id": "T2",
        "answers": {
            "personal_data": True,
            "health_data": True,
            "medical_purpose": False,
            "swedish_healthcare": False,
            "patient_records": False,
            "patient_safety": False,
            "ai_decision": False
        },
        "expected": ["GDPR"]
    },
    {
        "id": "T3",
        "answers": {
            "personal_data": False,
            "health_data": False,
            "medical_purpose": True,
            "swedish_healthcare": False,
            "patient_records": False,
            "patient_safety": False,
            "ai_decision": False
        },
        "expected": ["MDR"]
    },
    {
        "id": "T4",
        "answers": {
            "personal_data": True,
            "health_data": False,
            "medical_purpose": True,
            "swedish_healthcare": True,
            "patient_records": True,
            "patient_safety": True,
            "ai_decision": True
        },
        "expected": ["GDPR", "MDR", "HSL", "Patientdatalagen", "OSL", "Patientsäkerhetslagen", "AI_ACT"]
    },
    {
        "id": "T5",
        "answers": {
            "personal_data": False,
            "health_data": False,
            "medical_purpose": False,
            "swedish_healthcare": True,
            "patient_records": True,
            "patient_safety": False,
            "ai_decision": False
        },
        "expected": ["HSL", "Patientdatalagen", "OSL"]
    },
    {
        "id": "T6",
        "answers": {
            "personal_data": False,
            "health_data": False,
            "medical_purpose": False,
            "swedish_healthcare": False,
            "patient_records": False,
            "patient_safety": True,
            "ai_decision": False
        },
        "expected": ["Patientsäkerhetslagen"]
    },
    {
        "id": "T7",
        "answers": {
            "personal_data": False,
            "health_data": False,
            "medical_purpose": False,
            "swedish_healthcare": False,
            "patient_records": False,
            "patient_safety": False,
            "ai_decision": True
        },
        "expected": ["AI_ACT"]
    },
    {
        "id": "T8",
        "answers": {
            "personal_data": True,
            "health_data": True,
            "medical_purpose": True,
            "swedish_healthcare": False,
            "patient_records": False,
            "patient_safety": False,
            "ai_decision": False
        },
        "expected": ["GDPR", "MDR"]
    },
    {
        "id": "T9",
        "answers": {
            "personal_data": False,
            "health_data": False,
            "medical_purpose": False,
            "swedish_healthcare": True,
            "patient_records": True,
            "patient_safety": True,
            "ai_decision": False
        },
        "expected": ["HSL", "Patientdatalagen", "OSL", "Patientsäkerhetslagen"]
    },
    {
        "id": "T10",
        "answers": {
            "personal_data": True,
            "health_data": True,
            "medical_purpose": True,
            "swedish_healthcare": True,
            "patient_records": True,
            "patient_safety": True,
            "ai_decision": False
        },
        "expected": ["GDPR", "MDR", "HSL", "Patientdatalagen", "OSL", "Patientsäkerhetslagen"]
    }
]

# Run tests
print("=" * 60)
print("CHATBOT REGULATION TESTING")
print("=" * 60)

passed = 0
failed = 0

for test in test_cases:
  
    result = evaluate_regulations(test["answers"])
    result_set = set(result)
    expected_set = set(test["expected"])
    
    if result_set == expected_set:
        status = " PASS"
        passed += 1
    else:
        status = f" FAIL (Expected: {test['expected']}, Got: {result})"
        failed += 1
    
    print(f"{status} - {test['id']}")

print("=" * 60)
print(f"RESULTS: {passed} passed, {failed} failed")
print(f"ACCURACY: {(passed/(passed+failed))*100}%")
print("=" * 60)