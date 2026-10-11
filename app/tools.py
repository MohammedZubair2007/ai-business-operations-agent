
from datetime import date

from app.database import get_connection


def validate_month(month: str) -> None:
    """Validate a month in YYYY-MM format."""

    try:
        parsed = date.fromisoformat(f"{month}-01")
    except ValueError:
        raise ValueError("Month must use YYYY-MM format.")

    if parsed.strftime("%Y-%m") != month:
        raise ValueError("Month must use YYYY-MM format.")


def compare_monthly_sales(
    current_month: str,
    previous_month: str,
) -> dict:
    """Compare product revenue and units across two months."""

    validate_month(current_month)
    validate_month(previous_month)

    results = []

    with get_connection(read_only=True) as conn:
        for month in (current_month, previous_month):
            rows = conn.execute(
                """
                SELECT
                    product_id,
                    product_name,
                    SUM(units_sold) AS units,
                    ROUND(SUM(revenue), 2) AS revenue
                FROM sales
                WHERE sale_date >= ?
                  AND sale_date < date(?, '+1 month')
                GROUP BY product_id, product_name
                """,
                (month + "-01", month + "-01"),
            ).fetchall()

            results.append({
                row["product_id"]: dict(row)
                for row in rows
            })

    current, previous = results
    comparison = []

    for product_id in sorted(set(current) | set(previous)):
        now = current.get(product_id)
        before = previous.get(product_id)

        if not now or not before:
            product = now or before
            comparison.append({
                "product_id": product_id,
                "product_name": product["product_name"],
                "status": "insufficient_monthly_data",
            })
            continue

        previous_revenue = before["revenue"]
        current_revenue = now["revenue"]

        change_pct = None
        decline_pct = None

        if previous_revenue != 0:
            change_pct = round(
                (current_revenue - previous_revenue)
                / previous_revenue * 100,
                2,
            )
            decline_pct = round(-change_pct, 2)

        comparison.append({
            "product_id": product_id,
            "product_name": now["product_name"],
            "previous_revenue": previous_revenue,
            "current_revenue": current_revenue,
            "previous_units": before["units"],
            "current_units": now["units"],
            "change_pct": change_pct,
            "decline_pct": decline_pct,
            "status": (
                "declining"
                if current_revenue < previous_revenue
                else "not_declining"
            ),
        })

    return {
        "current_month": current_month,
        "previous_month": previous_month,
        "products": comparison,
    }

def create_action_draft(
    product_name: str,
    recommendation: str,
    rationale: str,
) -> dict:
    """Save a recommendation for human review."""

    values = [product_name, recommendation, rationale]

    if any(not value.strip() for value in values):
        raise ValueError("All draft fields are required.")

    if any(len(value) > 2000 for value in values):
        raise ValueError(
            "Draft fields must be 2000 characters or less."
        )

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO action_drafts (
                product_name,
                recommendation,
                rationale
            )
            VALUES (?, ?, ?)
            """,
            (product_name, recommendation, rationale),
        )

        draft_id = cursor.lastrowid
        conn.commit()

    return {
        "draft_id": draft_id,
        "status": "pending",
        "message": "Draft saved. Human approval is required.",
    }