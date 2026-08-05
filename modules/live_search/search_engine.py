from typing import Any, Callable

from .formatter import format_live_result
from .router import route
from .providers.crypto import get_crypto_price
from .providers.weather import get_weather
from .providers.stocks import get_stock_quote
from .providers.gold import get_gold_price


ProviderFunction = Callable[
    [str],
    dict[str, Any],
]


PROVIDERS: dict[
    str,
    ProviderFunction,
] = {
    "CRYPTO": get_crypto_price,
    "WEATHER": get_weather,
    "STOCK": get_stock_quote,
    "GOLD": get_gold_price,
}


def process(
    question: str,
) -> dict[str, Any]:
    result = route(question)

    if not result.get("live"):
        return result

    category = result.get("category")

    provider = PROVIDERS.get(
        category
    )

    if provider is None:
        result["data"] = {
            "success": False,
            "error": (
                f"No provider configured "
                f"for {category}"
            ),
        }

        result["prompt"] = None

        return result

    try:
        if category == "CRYPTO":
            provider_argument = (
                result.get("keyword")
                or question
            )
        else:
            provider_argument = question

        result["data"] = provider(
            provider_argument
        )

    except Exception as error:
        result["data"] = {
            "success": False,
            "error": str(error),
        }

    result["prompt"] = format_live_result(
        result
    )

    return result