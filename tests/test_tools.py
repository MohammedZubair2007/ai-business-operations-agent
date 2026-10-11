
from fastapi.testclient import TestClient

from app.main import app
from app.tools import compare_monthly_sales, validate_month


client = TestClient(app)


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


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_compare_monthly_sales_identifies_declining_products():
    result = compare_monthly_sales(
        current_month="2026-09",
        previous_month="2026-08",
    )

    products = {
        product["product_name"]: product
        for product in result["products"]
    }

    assert products["Wireless Mouse"]["change_pct"] == -50.0
    assert products["Wireless Mouse"]["status"] == "declining"
    assert products["USB-C Hub"]["status"] == "declining"


def test_compare_monthly_sales_identifies_growing_products():
    result = compare_monthly_sales(
        current_month="2026-09",
        previous_month="2026-08",
    )

    products = {
        product["product_name"]: product
        for product in result["products"]
    }

    assert products["Laptop Stand"]["change_pct"] == 10.0
    assert products["Laptop Stand"]["status"] == "not_declining"
    assert products["Keyboard"]["change_pct"] == 20.0
    assert products["Keyboard"]["status"] == "not_declining"


def test_approve_pending_draft():
    from app.tools import create_action_draft

    # Create a fresh pending draft for this test.
    draft = create_action_draft(
        product_name="Test Product",
        recommendation="Review pricing",
        rationale="Sales declined compared with the previous month.",
    )

    draft_id = draft["draft_id"]

    response = client.patch(
        f"/drafts/{draft_id}/decision",
        json={"decision": "approved"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "approved"


def test_reject_invalid_draft_decision():
    response = client.patch(
        "/drafts/999999/decision",
        json={"decision": "maybe"},
    )

    assert response.status_code == 422
