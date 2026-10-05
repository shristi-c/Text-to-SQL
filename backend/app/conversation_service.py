from typing import Any


# In-memory conversation storage.
# Each frontend session gets its own conversation context.
_conversations = {}


def get_empty_conversation():
    return {
        "question": None,
        "sql": None,
        "result": None,
        "domain": None,
    }


def get_conversation(session_id: str):
    """
    Return the conversation context for a session.

    If the session does not exist yet, return an empty context.
    """
    if not session_id:
        return get_empty_conversation()

    return _conversations.get(
        session_id,
        get_empty_conversation(),
    )


def update_conversation(
    session_id: str,
    question: str,
    sql: str,
    result: Any,
    domain: str,
):
    """
    Store the latest successful query context for a session.
    """
    if not session_id:
        return

    _conversations[session_id] = {
        "question": question,
        "sql": sql,
        "result": result,
        "domain": domain,
    }


def clear_conversation(session_id: str):
    """
    Clear the conversation context for a session.
    """
    if not session_id:
        return

    _conversations.pop(session_id, None)


def get_conversation_for_domain(
    session_id: str,
    domain: str,
):
    """
    Return conversation context only if it belongs
    to the currently selected domain.

    Changing domains automatically starts a fresh
    conversation context.
    """
    conversation = get_conversation(session_id)

    if not conversation["domain"]:
        return conversation

    if conversation["domain"] != domain:
        return get_empty_conversation()

    return conversation