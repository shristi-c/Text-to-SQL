from backend.app.llm_service import generate_sql
from backend.app.sql_validator import validate_sql
from backend.app.sql_service import execute_sql
from backend.app.answer_service import generate_answer


def process_question(question: str):
    if not question or not question.strip():
        return {
            "success": False,
            "error": "Question cannot be empty.",
        }

    # Generate SQL using Gemini
    try:
        sql = generate_sql(question)

    except Exception as e:
        return {
            "success": False,
            "question": question,
            "error": f"SQL generation failed: {str(e)}",
        }

    # Validate generated SQL
    validation = validate_sql(sql)

    if not validation["valid"]:
        return {
            "success": False,
            "question": question,
            "sql": sql,
            "error": validation["reason"],
        }

    # Execute validated SQL
    try:
        result = execute_sql(sql)

        # Convert database result into a natural-language answer
        answer = generate_answer(question, result)

        return {
            "success": True,
            "question": question,
            "sql": sql,
            "answer": answer,
            "data": result,
        }

    except Exception as e:
        return {
            "success": False,
            "question": question,
            "sql": sql,
            "error": f"SQL execution failed: {str(e)}",
        }