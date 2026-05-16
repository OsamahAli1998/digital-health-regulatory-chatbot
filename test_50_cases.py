import pandas as pd
from logic.decision_engine import evaluate_regulations

# Load test cases
df = pd.read_csv("test_cases.csv")

results = []

for _, row in df.iterrows():
    answers = {
        "personal_data": row["personal_data"] == "Y",
        "health_data": row["health_data"] == "Y",
        "medical_purpose": row["medical_purpose"] == "Y",
        "swedish_healthcare": row["swedish_healthcare"] == "Y",
        "patient_records": row["patient_records"] == "Y",
        "patient_safety": row["patient_safety"] == "Y",
        "ai_decision": row["ai_decision"] == "Y",
    }

    actual = evaluate_regulations(answers)
    expected = [x.strip() for x in row["Expected"].split(",")]

    actual_sorted = sorted(actual)
    expected_sorted = sorted(expected)

    passed = actual_sorted == expected_sorted

    results.append({
        "Test_ID": row["Test_ID"],
        "Expected": ", ".join(expected_sorted),
        "Actual": ", ".join(actual_sorted),
        "Pass": passed
    })

results_df = pd.DataFrame(results)
accuracy = results_df["Pass"].mean() * 100

print(results_df)
print(f"\nAccuracy: {accuracy:.2f}%")
print(f"Total tests: {len(results_df)}")
print(f"Passed: {results_df['Pass'].sum()}")
print(f"Failed: {len(results_df) - results_df['Pass'].sum()}")

results_df.to_csv("test_results.csv", index=False)
print("\n Results saved to test_results.csv")