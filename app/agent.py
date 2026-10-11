
import json

from ollama import chat

from app.tools import compare_monthly_sales, create_action_draft


def run_business_agent(
    current_month: str = "2026-09",
    previous_month: str = "2026-08",
) -> dict:
    """Analyze monthly sales and prepare recommendations for human review."""

    sales_data = compare_monthly_sales(
        current_month=current_month,
        previous_month=previous_month,
    )

    if not sales_data:
        return {
            "sales_analysis": [],
            "drafts": [],
            "message": "No sales data was found for these months.",
        }

    response = chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a business operations analyst. Analyze the "
                    "provided sales data and recommend practical actions. "
                    "Prioritize products with declining revenue. Use only "
                    "the supplied data. Do not claim actions were executed. "
                    "Return valid JSON in this format: "
                    '{"recommendations": [{"product_name": "...", '
                    '"recommendation": "...", "rationale": "..."}]}. '
                    "Recommend actions only for products with declining "
                    "revenue. Keep recommendations practical and specific."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Compare {current_month} with {previous_month}.\n"
                    f"Sales data:\n{json.dumps(sales_data, indent=2)}"
                ),
            },
        ],
        format={
            "type": "object",
            "properties": {
                "recommendations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "product_name": {"type": "string"},
                            "recommendation": {"type": "string"},
                            "rationale": {"type": "string"},
                        },
                        "required": [
                            "product_name",
                            "recommendation",
                            "rationale",
                        ],
                    },
                }
            },
            "required": ["recommendations"],
        },
        options={"temperature": 0.2},
    )

    content = response.message.content

    if not content:
        raise RuntimeError("The local AI returned an empty response.")

    result = json.loads(content)
    recommendations = result.get("recommendations", [])
    drafts = []

    for item in recommendations:
        product_name = item.get("product_name")
        recommendation = item.get("recommendation")
        rationale = item.get("rationale")

        if not all(
            isinstance(value, str) and value.strip()
            for value in (product_name, recommendation, rationale)
        ):
            continue

        draft = create_action_draft(
            product_name=product_name,
            recommendation=recommendation,
            rationale=rationale,
        )
        drafts.append(draft)

    return {
        "sales_analysis": sales_data,
        "drafts": drafts,
        "message": (
            "Analysis complete using local AI. Recommendations were saved "
            "as drafts and require human approval."
        ),
    }
