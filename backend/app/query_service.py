from backend.app.llm_service import generate_sql
from backend.app.sql_validator import validate_sql
from backend.app.sql_service import execute_sql
from backend.app.answer_service import generate_answer


ALLOWED_DOMAINS = {
    "it",
    "retail",
    "airline",
}


def process_question(question: str, domain: str):
    if not question or not question.strip():
        return {
            "success": False,
            "error": "Question cannot be empty.",
        }

    domain = domain.lower().strip()

    if domain not in ALLOWED_DOMAINS:
        return {
            "success": False,
            "error": (
                f"Invalid domain '{domain}'. "
                "Choose it, retail, or airline."
            ),
        }

    try:
        sql = generate_sql(question, domain)

    except Exception as e:
        return {
            "success": False,
            "question": question,
            "domain": domain,
            "error": f"SQL generation failed: {str(e)}",
        }

    validation = validate_sql(sql)

    if not validation["valid"]:
        return {
            "success": False,
            "question": question,
            "domain": domain,
            "sql": sql,
            "error": validation["reason"],
        }

    try:
        result = execute_sql(sql)

        answer = generate_answer(question, result)

        return {
            "success": True,
            "question": question,
            "domain": domain,
            "sql": sql,
            "answer": answer,
            "data": result,
        }

    except Exception as e:
        return {
            "success": False,
            "question": question,
            "domain": domain,
            "sql": sql,
            "error": f"SQL execution failed: {str(e)}",
        }