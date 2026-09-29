from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_schema():
    response = client.get("/schema")

    assert response.status_code == 200

    data = response.json()

    assert "it" in data
    assert "retail" in data
    assert "airline" in data


def test_validate_safe_sql():
    response = client.post(
        "/validate-sql",
        params={
            "sql": "SELECT * FROM retail.customers"
        },
    )

    assert response.status_code == 200
    assert response.json()["valid"] is True


def test_validate_delete():
    response = client.post(
        "/validate-sql",
        params={
            "sql": "DELETE FROM retail.customers"
        },
    )

    assert response.status_code == 200
    assert response.json()["valid"] is False


def test_validate_wrong_schema():
    response = client.post(
        "/validate-sql",
        params={
            "sql": "SELECT * FROM public.users"
        },
    )

    assert response.status_code == 200
    assert response.json()["valid"] is False


def test_execute_sql():
    response = client.post(
        "/execute-sql",
        params={
            "sql": "SELECT COUNT(*) FROM retail.customers"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["data"]["row_count"] == 1


