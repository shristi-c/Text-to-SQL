import os
import sys
import json


# Add project root to Python path
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, PROJECT_ROOT)


from backend.app.sql_service import execute_sql


questions_file = os.path.join(
    PROJECT_ROOT,
    "evaluation",
    "questions.json",
)


with open(questions_file, encoding="utf-8") as file:
    questions = json.load(file)


passed = 0
failed = 0


for item in questions:
    question_id = item["id"]
    question = item["question"]
    sql = item["expected_sql"]

    try:
        result = execute_sql(sql)

        print(
            f"[PASS] {question_id}: "
            f"{question} -> {result['row_count']} rows"
        )

        passed += 1

    except Exception as e:
        print(
            f"[FAIL] {question_id}: "
            f"{question}"
        )
        print(f"       SQL: {sql}")
        print(f"       Error: {e}")
        print()

        failed += 1


print()
print("=" * 60)
print(f"Total:  60")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print("=" * 60)