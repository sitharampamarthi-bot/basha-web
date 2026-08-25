from __future__ import annotations

from typing import Any, Callable

from .formatter import format_live_result
from .router import route

from .providers.crypto import get_crypto_price
from .providers.weather import get_weather
from .providers.stocks import get_stock_quote
from .providers.gold import get_gold_price

from .providers.currency import get_currency_rate
from .providers.fuel import get_fuel_price
from .providers.google_news import get_news
from .providers.sports import get_sports
from .providers.holidays import get_holidays
from .providers.movies import search_movies
from .providers.wikipedia import search_wikipedia
from .providers.youtube import search_youtube
from .providers.calculator import calculate
from .providers.unit_converter import convert_units

from .providers.travel import (
    get_train,
    get_bus,
    get_flight,
)


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

    "CURRENCY": get_currency_rate,
    "FUEL": get_fuel_price,
    "NEWS": get_news,
    "SPORTS": get_sports,
    "HOLIDAY": get_holidays,
    "MOVIE": search_movies,
    "WIKIPEDIA": search_wikipedia,
    "YOUTUBE": search_youtube,
    "CALCULATOR": calculate,
    "UNIT": convert_units,

    "TRAIN": get_train,
    "BUS": get_bus,
    "FLIGHT": get_flight,
}


def process(
    question: str,
) -> dict[str, Any]:

    result = route(
        question
    )

    if not result.get("live"):
        return result

    category = result.get(
        "category"
    )

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

        # Crypto provider currently works better
        # when we pass the detected coin keyword.
        if category == "CRYPTO":

            provider_argument = (
                result.get("keyword")
                or question
            )

        else:

            # All other providers need full question
            # because city/company/topic/route etc.
            # may be present in the sentence.
            provider_argument = question

        result["data"] = provider(
            provider_argument
        )

    except Exception as error:

        result["data"] = {
            "success": False,
            "error": str(error),
        }

    result["prompt"] = (
        format_live_result(
            result
        )
    )

    return result