from typing import Any


def get_gold_price(
    question: str = "",
) -> dict[str, Any]:
    return {
        "success": False,
        "error": (
            "Gold provider is not configured yet."
        ),
        "query": question,
    }