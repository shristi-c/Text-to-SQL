from backend.app.conversation_service import (
    get_conversation,
    get_conversation_for_domain,
    update_conversation,
    clear_conversation,
)


def test_new_conversation_is_empty():
    conversation = get_conversation("test-session")

    assert conversation["question"] is None
    assert conversation["sql"] is None
    assert conversation["result"] is None
    assert conversation["domain"] is None


def test_conversation_can_be_updated():
    update_conversation(
        session_id="test-session",
        question="How many customers are there?",
        sql="SELECT COUNT(*) FROM retail.customers;",
        result={
            "columns": ["count"],
            "rows": [[793]],
            "row_count": 1,
        },
        domain="retail",
    )

    conversation = get_conversation("test-session")

    assert conversation["question"] == (
        "How many customers are there?"
    )

    assert conversation["sql"] == (
        "SELECT COUNT(*) FROM retail.customers;"
    )

    assert conversation["result"]["rows"] == [[793]]

    assert conversation["domain"] == "retail"


def test_domain_change_returns_empty_context():
    conversation = get_conversation_for_domain(
        "test-session",
        "airline",
    )

    assert conversation["question"] is None
    assert conversation["sql"] is None
    assert conversation["result"] is None
    assert conversation["domain"] is None


def test_same_domain_returns_context():
    conversation = get_conversation_for_domain(
        "test-session",
        "retail",
    )

    assert conversation["question"] == (
        "How many customers are there?"
    )

    assert conversation["domain"] == "retail"


def test_conversation_can_be_cleared():
    clear_conversation("test-session")

    conversation = get_conversation("test-session")

    assert conversation["question"] is None
    assert conversation["sql"] is None
    assert conversation["result"] is None
    assert conversation["domain"] is None