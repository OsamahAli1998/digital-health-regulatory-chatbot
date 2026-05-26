import itertools
import csv
from logic.decision_engine import evaluate_regulations

# Define expected regulations
def get_expected(answers):
    triggered = []

    if answers["personal_data"] or answers["health_data"]:
        triggered.append("GDPR")

    if answers["medical_purpose"]:
        triggered.append("MDR")

    if answers["swedish_healthcare"]:
        triggered.append("HSL")

    if answers["patient_records"]:
        triggered.append("Patientdatalagen")
        triggered.append("OSL")

    if answers["patient_safety"]:
        triggered.append("Patientsäkerhetslagen")

    if answers["ai_decision"]:
        triggered.append("AI_ACT")

    return sorted(list(dict.fromkeys(triggered)))


question_ids = [
    "personal_data",
    "health_data",
    "medical_purpose",
    "swedish_healthcare",
    "patient_records",
    "patient_safety",
    "ai_decision"
]

results = []
passed = 0
failed = 0

for i, combo in enumerate(itertools.product([False, True], repeat=7), start=1):
    answers = dict(zip(question_ids, combo))

    actual = sorted(evaluate_regulations(answers))
    expected = get_expected(answers)

    is_pass = actual == expected

    if is_pass:
        passed += 1
    else:
        failed += 1

    results.append({
        "test_id": f"T{i}",
        **answers,
        "expected": ", ".join(expected),
        "actual": ", ".join(actual),
        "pass": "PASS" if is_pass else "FAIL"
    })

with open("128_test_results.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("Done. 128 test cases created and tested.")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Accuracy: {(passed / 128) * 100:.2f}%")