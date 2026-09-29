import os
import sys
import json
import time
from collections import defaultdict


# Add project root to Python path
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, PROJECT_ROOT)


from backend.app.llm_service import generate_sql
from backend.app.sql_validator import validate_sql
from backend.app.sql_service import execute_sql


QUESTIONS_FILE = os.path.join(
    PROJECT_ROOT,
    "evaluation",
    "questions.json",
)


def normalize_result(result):
    columns = [
        str(column).lower()
        for column in result.get("columns", [])
    ]

    rows = result.get("rows", [])

    normalized_rows = []

    for row in rows:
        normalized_rows.append(
            tuple(
                str(value) if value is not None else None
                for value in row
            )
        )

    normalized_rows.sort(
        key=lambda row: tuple(
            "" if value is None else str(value)
            for value in row
        )
    )

    return {
        "columns": columns,
        "rows": normalized_rows,
    }


def results_match(expected, generated):
    return (
        normalize_result(expected)
        == normalize_result(generated)
    )


with open(
    QUESTIONS_FILE,
    encoding="utf-8",
) as file:
    questions = json.load(file)


total = len(questions)

sql_generated = 0
sql_generation_failed = 0
validation_passed = 0
validation_failed = 0
execution_passed = 0
execution_failed = 0
correct = 0
incorrect = 0


results = []


# Domain statistics
domain_stats = defaultdict(
    lambda: {
        "total": 0,
        "correct": 0,
        "incorrect": 0,
        "generation_failed": 0,
        "validation_failed": 0,
        "execution_failed": 0,
    }
)


print("=" * 70)
print("TEXT-TO-SQL MODEL EVALUATION")
print("=" * 70)
print(f"Total questions: {total}")
print()


for item in questions:

    question_id = item["id"]
    domain = item["domain"]
    question = item["question"]
    expected_sql = item["expected_sql"]

    domain_stats[domain]["total"] += 1

    print(
        f"[{question_id}/{total}] {question}"
    )

    record = {
        "id": question_id,
        "domain": domain,
        "question": question,
        "expected_sql": expected_sql,
        "generated_sql": None,
        "valid": False,
        "executed": False,
        "correct": False,
        "error": None,
    }

    # ------------------------------------------------------
    # Generate SQL
    # ------------------------------------------------------

    try:

        start_time = time.time()

        generated_sql = generate_sql(question)

        generation_time = time.time() - start_time

        record["generated_sql"] = generated_sql
        record["generation_time_seconds"] = round(
            generation_time,
            2,
        )

        sql_generated += 1

        print(
            f"    Generated SQL: {generated_sql}"
        )

    except Exception as e:

        sql_generation_failed += 1
        domain_stats[domain]["generation_failed"] += 1

        record["error"] = (
            f"SQL generation failed: {str(e)}"
        )

        print(
            f"    [GENERATION FAILED] {e}"
        )

        results.append(record)
        continue

    # ------------------------------------------------------
    # Validate SQL
    # ------------------------------------------------------

    try:

        validation = validate_sql(
            generated_sql
        )

        if not validation["valid"]:

            validation_failed += 1
            domain_stats[domain]["validation_failed"] += 1

            record["error"] = (
                f"Validation failed: "
                f"{validation['reason']}"
            )

            print(
                f"    [VALIDATION FAILED] "
                f"{validation['reason']}"
            )

            results.append(record)
            continue

        validation_passed += 1
        record["valid"] = True

    except Exception as e:

        validation_failed += 1
        domain_stats[domain]["validation_failed"] += 1

        record["error"] = (
            f"Validation error: {str(e)}"
        )

        print(
            f"    [VALIDATION ERROR] {e}"
        )

        results.append(record)
        continue

    # ------------------------------------------------------
    # Execute SQL
    # ------------------------------------------------------

    try:

        generated_result = execute_sql(
            generated_sql
        )

        expected_result = execute_sql(
            expected_sql
        )

        execution_passed += 1
        record["executed"] = True

    except Exception as e:

        execution_failed += 1
        domain_stats[domain]["execution_failed"] += 1

        record["error"] = (
            f"Execution failed: {str(e)}"
        )

        print(
            f"    [EXECUTION FAILED] {e}"
        )

        results.append(record)
        continue

    # ------------------------------------------------------
    # Compare results
    # ------------------------------------------------------

    if results_match(
        expected_result,
        generated_result,
    ):

        correct += 1
        domain_stats[domain]["correct"] += 1

        record["correct"] = True

        print("    [CORRECT]")

    else:

        incorrect += 1
        domain_stats[domain]["incorrect"] += 1

        print("    [INCORRECT]")

        print(
            f"    Expected: {expected_result}"
        )

        print(
            f"    Generated: {generated_result}"
        )

    results.append(record)

    print()


# ----------------------------------------------------------
# Overall accuracy
# ----------------------------------------------------------

accuracy = (
    correct / total * 100
    if total > 0
    else 0
)


# ----------------------------------------------------------
# Domain accuracy
# ----------------------------------------------------------

domain_results = {}

for domain, stats in domain_stats.items():

    domain_total = stats["total"]

    domain_accuracy = (
        stats["correct"] / domain_total * 100
        if domain_total > 0
        else 0
    )

    domain_results[domain] = {
        **stats,
        "accuracy_percent": round(
            domain_accuracy,
            2,
        ),
    }


# ----------------------------------------------------------
# Print final results
# ----------------------------------------------------------

print()
print("=" * 70)
print("OVERALL EVALUATION RESULTS")
print("=" * 70)

print(f"Total questions:        {total}")
print(f"SQL generated:          {sql_generated}")
print(f"Generation failures:    {sql_generation_failed}")
print(f"Validation passed:      {validation_passed}")
print(f"Validation failed:      {validation_failed}")
print(f"Execution passed:       {execution_passed}")
print(f"Execution failed:       {execution_failed}")
print(f"Correct answers:        {correct}")
print(f"Incorrect answers:      {incorrect}")
print(f"Accuracy:               {accuracy:.2f}%")

print()
print("=" * 70)
print("DOMAIN-WISE RESULTS")
print("=" * 70)

for domain, stats in domain_results.items():

    print(
        f"{domain.upper():10} "
        f"{stats['correct']}/{stats['total']} "
        f"correct "
        f"({stats['accuracy_percent']:.2f}%)"
    )

print("=" * 70)


# ----------------------------------------------------------
# Save detailed results
# ----------------------------------------------------------

results_file = os.path.join(
    PROJECT_ROOT,
    "evaluation",
    "evaluation_results.json",
)


with open(
    results_file,
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        {
            "total_questions": total,
            "sql_generated": sql_generated,
            "generation_failures": sql_generation_failed,
            "validation_passed": validation_passed,
            "validation_failed": validation_failed,
            "execution_passed": execution_passed,
            "execution_failed": execution_failed,
            "correct": correct,
            "incorrect": incorrect,
            "accuracy_percent": round(
                accuracy,
                2,
            ),
            "domain_results": domain_results,
            "results": results,
        },
        file,
        indent=2,
        ensure_ascii=False,
    )


print()
print(
    "Detailed results saved to:"
)
print(
    "evaluation\\evaluation_results.json"
)