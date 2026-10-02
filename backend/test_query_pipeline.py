from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app import query_service


client = TestClient(app)


def test_query_pipeline(monkeypatch):
    """
    Test the complete /query pipeline without calling Gemini.
    """

    def fake_generate_sql(question, domain):
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
    assert data["sql"] == "SELECT COUNT(*) FROM retail.customers"
    assert data["data"]["rows"] == [[793]]
    assert data["answer"] == "The answer is 793."