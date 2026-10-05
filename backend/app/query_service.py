import time

from backend.app.database import save_query_history
from backend.app.llm_service import generate_sql
from backend.app.sql_correction_service import correct_sql
from backend.app.sql_validator import validate_sql
from backend.app.sql_service import execute_sql
from backend.app.answer_service import generate_answer
from backend.app.conversation_service import (
    get_conversation_for_domain,
    update_conversation,
)


ALLOWED_DOMAINS = {
    "it",
    "retail",
    "airline",
}


def process_question(
    question: str,
    domain: str,
    session_id: str = None,
):
    if not question or not question.strip():
        return {
            "success": False,
            "error": "Question cannot be empty.",
        }

    domain = domain.lower().strip()

    if domain not in ALLOWED_DOMAINS:
        return {
            "success": False,
            "question": question,
            "domain": domain,
            "error": (
                f"Invalid domain '{domain}'. "
                "Choose it, retail, or airline."
            ),
        }

    # STEP 1: Get previous conversation context
    conversation_context = get_conversation_for_domain(
        session_id=session_id,
        domain=domain,
    )

    # STEP 2: Generate SQL
    try:
        sql = generate_sql(
            question=question,
            domain=domain,
            conversation_context=conversation_context,
        )
    except Exception as e:
        return {
            "success": False,
            "question": question,
            "domain": domain,
            "error": f"SQL generation failed: {str(e)}",
        }

    # STEP 3: Validate generated SQL
    validation = validate_sql(sql)

    if not validation["valid"]:
        return {
            "success": False,
            "question": question,
            "domain": domain,
            "sql": sql,
            "error": validation["reason"],
        }

    # STEP 4: Execute SQL
    try:
        start_time = time.perf_counter()

        result = execute_sql(sql)

        execution_time_ms = (
            time.perf_counter() - start_time
        ) * 1000

        answer = generate_answer(
            question,
            result,
        )

        # Save permanent query history
        save_query_history(
            question=question,
            domain=domain,
            sql=sql,
            answer=answer,
            result=result,
            row_count=result["row_count"],
            execution_time_ms=execution_time_ms,
        )

        # Update active conversation context
        update_conversation(
            session_id=session_id,
            question=question,
            sql=sql,
            result=result,
            domain=domain,
        )

        return {
            "success": True,
            "question": question,
            "domain": domain,
            "sql": sql,
            "answer": answer,
            "data": result,
            "execution_time_ms": execution_time_ms,
            "corrected": False,
        }

    # STEP 5: SQL failed → attempt automatic correction
    except Exception as original_error:

        original_error_message = str(original_error)

        try:
            corrected_sql = correct_sql(
                question=question,
                domain=domain,
                failed_sql=sql,
                error_message=original_error_message,
            )
        except Exception as correction_error:
            return {
                "success": False,
                "question": question,
                "domain": domain,
                "sql": sql,
                "error": (
                    f"SQL execution failed: "
                    f"{original_error_message}. "
                    f"Automatic SQL correction also failed: "
                    f"{str(correction_error)}"
                ),
            }

        # STEP 6: Validate corrected SQL
        corrected_validation = validate_sql(
            corrected_sql
        )

        if not corrected_validation["valid"]:
            return {
                "success": False,
                "question": question,
                "domain": domain,
                "sql": corrected_sql,
                "error": (
                    "Corrected SQL failed validation: "
                    f"{corrected_validation['reason']}"
                ),
                "original_sql": sql,
                "original_error": original_error_message,
            }

        # STEP 7: Execute corrected SQL
        try:
            correction_start_time = time.perf_counter()

            corrected_result = execute_sql(
                corrected_sql
            )

            corrected_execution_time_ms = (
                time.perf_counter() - correction_start_time
            ) * 1000

            corrected_answer = generate_answer(
                question,
                corrected_result,
            )

            # Save corrected query to permanent history
            save_query_history(
                question=question,
                domain=domain,
                sql=corrected_sql,
                answer=corrected_answer,
                result=corrected_result,
                row_count=corrected_result["row_count"],
                execution_time_ms=corrected_execution_time_ms,
                original_sql=sql,
                original_error=original_error_message,
                corrected=True,
            )

            # Update active conversation with corrected query
            update_conversation(
                session_id=session_id,
                question=question,
                sql=corrected_sql,
                result=corrected_result,
                domain=domain,
            )

            return {
                "success": True,
                "question": question,
                "domain": domain,
                "sql": corrected_sql,
                "answer": corrected_answer,
                "data": corrected_result,
                "execution_time_ms": corrected_execution_time_ms,
                "corrected": True,
                "original_sql": sql,
                "original_error": original_error_message,
            }

        except Exception as corrected_error:
            return {
                "success": False,
                "question": question,
                "domain": domain,
                "sql": corrected_sql,
                "error": (
                    "Original SQL failed: "
                    f"{original_error_message}. "
                    "Corrected SQL also failed: "
                    f"{str(corrected_error)}"
                ),
                "original_sql": sql,
                "original_error": original_error_message,
            }