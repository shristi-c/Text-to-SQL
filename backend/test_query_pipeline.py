from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app import query_service


client = TestClient(app)


def test_query_pipeline(monkeypatch):
    """
    Test the complete /query pipeline without calling the LLM.
    """

    def fake_generate_sql(
        question,
        domain,
        conversation_context=None,
    ):
        return "SELECT COUNT(*) FROM retail.customers"

    monkeypatch.setattr(
        query_service,
        "generate_sql",
        fake_generate_sql,
    )

    response = client.post(
        "/query",
        params={
            "question": "How many customers are there?",
            "domain": "retail",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["domain"] == "retail"
    assert data["question"] == "How many customers are there?"
    assert data["data"]["rows"] == [[793]]