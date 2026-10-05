from backend.app.sql_correction_service import correct_sql
from backend.app.sql_validator import validate_sql
from backend.app.sql_service import execute_sql
from backend.app.database import save_query_history
from backend.app.answer_service import generate_answer


def test_history_correction():
    question = "How many customers are there?"
    domain = "retail"

    failed_sql = "SELECT COUNT(*) FROM retail.customer;"

    error_message = (
        'relation "retail.customer" does not exist'
    )

    # Generate corrected SQL
    corrected_sql = correct_sql(
        question=question,
        domain=domain,
        failed_sql=failed_sql,
        error_message=error_message,
    )

    print("\nORIGINAL SQL:")
    print(failed_sql)

    print("\nCORRECTED SQL:")
    print(corrected_sql)

    # Validate corrected SQL
    validation = validate_sql(corrected_sql)

    print("\nVALIDATION:")
    print(validation)

    assert validation["valid"] is True

    # Execute corrected SQL
    result = execute_sql(corrected_sql)

    print("\nRESULT:")
    print(result)

    assert result["row_count"] == 1
    assert result["rows"][0][0] == 793

    # Generate answer
    answer = generate_answer(
        question,
        result,
    )

    # Save correction information in history
    save_query_history(
        question=question,
        domain=domain,
        sql=corrected_sql,
        answer=answer,
        result=result,
        row_count=result["row_count"],
        execution_time_ms=0,
        original_sql=failed_sql,
        original_error=error_message,
        corrected=True,
    )

    print("\nHISTORY SAVED:")
    print("corrected=True")