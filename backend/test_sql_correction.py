from backend.app.sql_correction_service import correct_sql


def test_sql_correction():
    question = "How many customers are there?"
    domain = "retail"

    failed_sql = """
    SELECT COUNT(*) FROM retail.customer;
    """

    error_message = (
        'relation "retail.customer" does not exist'
    )

    corrected_sql = correct_sql(
        question=question,
        domain=domain,
        failed_sql=failed_sql,
        error_message=error_message,
    )

    print("\nCorrected SQL:")
    print(corrected_sql)

    assert corrected_sql
    assert "SELECT" in corrected_sql.upper()