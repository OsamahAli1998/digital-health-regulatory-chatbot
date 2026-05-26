import itertools
import csv
from logic.decision_engine import evaluate_regulations

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

for i, combo in enumerate(itertools.product([False, True], repeat=7), start=1):
    answers = dict(zip(question_ids, combo))
    regulations = evaluate_regulations(answers)

    results.append({
        "test_id": f"T{i}",
        **answers,
        "triggered_regulations": ", ".join(regulations)
    })

with open("128_test_results.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("Done. 128 test cases created and tested.")
