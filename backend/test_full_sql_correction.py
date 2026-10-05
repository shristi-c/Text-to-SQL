from backend.app.sql_correction_service import correct_sql
from backend.app.sql_validator import validate_sql
from backend.app.sql_service import execute_sql


def test_full_sql_correction():
    question = "How many customers are there?"
    domain = "retail"

    failed_sql = "SELECT COUNT(*) FROM retail.customer;"

    error_message = (
        'relation "retail.customer" does not exist'
    )

    corrected_sql = correct_sql(
        question=question,
        domain=domain,
        failed_sql=failed_sql,
        error_message=error_message,
    )

    print("\nCORRECTED SQL:")
    print(corrected_sql)

    validation = validate_sql(corrected_sql)

    print("\nVALIDATION:")
    print(validation)

    assert validation["valid"] is True

    result = execute_sql(corrected_sql)

    print("\nRESULT:")
    print(result)

    assert result["row_count"] == 1
    assert result["rows"][0][0] == 793