from backend.app.query_service import process_question
from backend.app.conversation_service import (
    get_conversation,
    clear_conversation,
)


def test_followup_pipeline():
    session_id = "followup-test-session"

    # Start with a clean conversation
    clear_conversation(session_id)

    # -------------------------------------------------
    # QUESTION 1
    # -------------------------------------------------

    first_result = process_question(
        question="How many customers are there?",
        domain="retail",
        session_id=session_id,
    )

    print("\nFIRST QUESTION:")
    print(first_result)

    assert first_result["success"] is True
    assert first_result["data"]["rows"] == [[793]]

    # -------------------------------------------------
    # CHECK CONVERSATION CONTEXT
    # -------------------------------------------------

    conversation = get_conversation(session_id)

    print("\nSAVED CONVERSATION:")
    print(conversation)

    assert conversation["question"] == (
        "How many customers are there?"
    )

    assert conversation["domain"] == "retail"

    assert conversation["sql"]

    assert conversation["result"]["rows"] == [[793]]

    # -------------------------------------------------
    # QUESTION 2 — FOLLOW-UP
    # -------------------------------------------------

    second_result = process_question(
        question="Now show their average order value.",
        domain="retail",
        session_id=session_id,
    )

    print("\nFOLLOW-UP QUESTION:")
    print(second_result)

    assert second_result["success"] is True

    assert second_result["sql"]

    assert "SELECT" in second_result["sql"].upper()

    # -------------------------------------------------
    # CHECK UPDATED CONTEXT
    # -------------------------------------------------

    updated_conversation = get_conversation(
        session_id
    )

    print("\nUPDATED CONVERSATION:")
    print(updated_conversation)

    assert updated_conversation["question"] == (
        "Now show their average order value."
    )

    assert updated_conversation["domain"] == "retail"

    assert updated_conversation["sql"] == (
        second_result["sql"]
    )

    assert updated_conversation["result"] == (
        second_result["data"]
    )

    # Clean up after the test
    clear_conversation(session_id)