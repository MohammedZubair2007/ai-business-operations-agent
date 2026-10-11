from app.tools import validate_month


def test_validate_month_accepts_valid_month():
    validate_month("2026-09")


def test_validate_month_rejects_invalid_format():
    try:
        validate_month("September 2026")
    except ValueError:
        return

    assert False, "Expected ValueError for invalid format"


def test_validate_month_rejects_invalid_month():
    try:
        validate_month("2026-13")
    except ValueError:
        return

    assert False, "Expected ValueError for invalid month"

    
    
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"