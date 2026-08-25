from __future__ import annotations

import re
from typing import Any


CRYPTO_KEYWORDS = [
    "bitcoin",
    "btc",
    "ethereum",
    "eth",
    "solana",
    "sol",
    "dogecoin",
    "doge",
    "bnb",
    "xrp",
    "cardano",
    "ada",
    "crypto",
    "cryptocurrency",
    "usdt",
    "binance",

    "బిట్‌కాయిన్",
    "ఎథీరియం",
    "క్రిప్టో",
]


WEATHER_KEYWORDS = [
    "weather",
    "temperature",
    "rain",
    "forecast",
    "humidity",
    "wind",
    "climate",

    "వాతావరణం",
    "వర్షం",
    "వాన",
    "ఉష్ణోగ్రత",
    "హ్యూమిడిటీ",
    "గాలి",
    "వెదర్",
    "టెంపరేచర్",
]


GOLD_KEYWORDS = [
    "gold rate",
    "gold price",
    "silver rate",
    "silver price",
    "22 carat gold",
    "24 carat gold",
    "22k gold",
    "24k gold",
    "gold",
    "silver",

    "బంగారం ధర",
    "బంగారం రేటు",
    "వెండి ధర",
    "వెండి రేటు",
    "22 క్యారెట్ల బంగారం",
    "24 క్యారెట్ల బంగారం",
    "బంగారం",
    "వెండి",
]


CURRENCY_KEYWORDS = [
    "usd inr",
    "eur inr",
    "gbp inr",
    "aed inr",
    "sar inr",

    "dollar rate",
    "currency rate",
    "exchange rate",
    "convert currency",

    "usd",
    "inr",
    "eur",
    "gbp",
    "aed",
    "sar",

    "dollar",
    "rupee",
    "currency",

    "డాలర్ ధర",
    "డాలర్",
    "రూపాయి",
    "కరెన్సీ",
]


FUEL_KEYWORDS = [
    "petrol price",
    "diesel price",
    "petrol rate",
    "diesel rate",
    "fuel price",
    "cng price",

    "petrol",
    "diesel",
    "fuel",
    "cng",

    "పెట్రోల్ ధర",
    "డీజిల్ ధర",
    "పెట్రోల్",
    "డీజిల్",
    "ఇంధనం",
]


STOCK_KEYWORDS = [
    "bank nifty",
    "banknifty",
    "nifty bank",
    "nifty 50",
    "nifty",
    "sensex",

    "బ్యాంక్ నిఫ్టీ",
    "నిఫ్టీ",
    "సెన్సెక్స్",

    "share price",
    "stock price",
    "share rate",
    "stock rate",
    "market price",
    "current price",
    "live price",
    "today price",
    "equity price",
    "nse price",
    "bse price",

    "share",
    "stock",
    "equity",
    "nse",
    "bse",

    "షేర్ ధర",
    "స్టాక్ ధర",
    "ప్రస్తుత ధర",
    "లైవ్ ధర",
    "మార్కెట్ ధర",
    "ధర ఎంత",
    "షేర్",
    "స్టాక్",
]


NEWS_KEYWORDS = [
    "today news",
    "latest news",
    "breaking news",
    "news",
    "headlines",
    "breaking",

    "వార్తలు",
    "న్యూస్",
    "తాజా వార్తలు",
]


SPORTS_KEYWORDS = [
    # Common sports intents
    "live score",
    "live match",
    "match score",
    "match today",
    "today match",
    "next match",
    "sports schedule",
    "sports result",
    "sports ranking",

    # Cricket
    "cricket",
    "ipl",
    "t20",
    "t20i",
    "odi",
    "test match",

    # Football
    "football",
    "soccer",
    "fifa",
    "isl",

    # Hockey
    "hockey",
    "field hockey",

    # Badminton
    "badminton",
    "bwf",

    # Kabaddi
    "kabaddi",
    "pro kabaddi",
    "pkl",

    # Tennis
    "tennis",
    "atp",
    "wta",

    # Chess
    "chess",
    "fide",

    # Athletics
    "athletics",
    "javelin",

    # Wrestling
    "wrestling",

    # Boxing
    "boxing",

    # Shooting
    "shooting",

    # Table tennis
    "table tennis",

    # Volleyball
    "volleyball",

    # Basketball
    "basketball",

    # Formula 1
    "formula 1",
    "formula one",

    # Telugu
    "క్రికెట్",
    "ఐపీఎల్",
    "స్కోర్",
    "మ్యాచ్",
    "ఫుట్‌బాల్",
    "హాకీ",
    "బ్యాడ్మింటన్",
    "కబడ్డీ",
    "టెన్నిస్",
    "చెస్",
    "అథ్లెటిక్స్",
    "రెజ్లింగ్",
    "బాక్సింగ్",
    "షూటింగ్",
    "టేబుల్ టెన్నిస్",
    "వాలీబాల్",
    "బాస్కెట్‌బాల్",
]


HOLIDAY_KEYWORDS = [
    "public holiday",
    "bank holiday",
    "holiday list",
    "next holiday",
    "festival holiday",
    "holidays",
    "holiday",

    "సెలవులు",
    "సెలవు",
    "హాలిడే",
    "పబ్లిక్ హాలిడే",
]


MOVIE_KEYWORDS = [
    "movie details",
    "latest movie",
    "release date",
    "movie rating",
    "movies",
    "movie",
    "film",
    "cinema",

    "సినిమాలు",
    "సినిమా",
    "మూవీ",
    "రిలీజ్",
]


WIKIPEDIA_KEYWORDS = [
    "wikipedia",
    "wiki",

    "వికీపీడియా",
    "వికీ",
]


YOUTUBE_KEYWORDS = [
    "youtube video",
    "youtube videos",
    "youtube search",
    "youtube",
    "video search",

    "యూట్యూబ్",
]


TRAIN_KEYWORDS = [
    "train booking",
    "book train",
    "train ticket",
    "train route",
    "train from",

    "రైలు టికెట్",
    "ట్రైన్ బుకింగ్",
    "రైలు",
]


BUS_KEYWORDS = [
    "bus booking",
    "book bus",
    "bus ticket",
    "bus from",

    "బస్ టికెట్",
    "బస్ బుకింగ్",
    "బస్సు",
]


FLIGHT_KEYWORDS = [
    "flight booking",
    "book flight",
    "air ticket",
    "flight ticket",
    "flight from",
    "air booking",

    "విమాన టికెట్",
    "ఫ్లైట్ బుకింగ్",
    "విమానం",
]


UNIT_KEYWORDS = [
    "unit converter",
    "unit conversion",

    "km to",
    "kg to",
    "cm to",
    "mm to",
    "miles to",
    "feet to",
    "inch to",
    "celsius to",
    "fahrenheit to",
    "litre to",
    "liter to",

    "యూనిట్ కన్వర్ట్",
]


CALCULATOR_KEYWORDS = [
    "calculate",
    "calculator",
    "compute",

    "క్యాలిక్యులేట్",
    "లెక్క",
    "ఎంత అవుతుంది",
]


def normalize_text(
    value: Any,
) -> str:

    return re.sub(
        r"\s+",
        " ",
        str(value or "")
        .casefold()
        .strip(),
    )


def contains_keyword(
    question: str,
    keyword: str,
) -> bool:

    q = normalize_text(question)

    word = normalize_text(keyword)

    if not q or not word:
        return False

    if re.fullmatch(
        r"[a-z0-9&.\-\s]+",
        word,
    ):
        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(word)
            + r"(?![a-z0-9])"
        )

        return (
            re.search(
                pattern,
                q,
                flags=re.IGNORECASE,
            )
            is not None
        )

    return word in q


def find_keyword(
    question: str,
    keywords: list[str],
) -> str | None:

    for keyword in sorted(
        keywords,
        key=len,
        reverse=True,
    ):
        if contains_keyword(
            question,
            keyword,
        ):
            return keyword

    return None


def looks_like_calculation(
    question: str,
) -> bool:

    text = normalize_text(
        question
    )

    if not text:
        return False

    cleaned = (
        text
        .replace("×", "*")
        .replace("÷", "/")
    )

    return (
        re.fullmatch(
            r"[0-9\s()+\-*/%.^]+",
            cleaned,
        )
        is not None
    )


def analyze_question(
    question: str,
) -> dict[str, Any]:

    text = normalize_text(
        question
    )

    if not text:
        return {
            "live": False,
            "category": "GENERAL",
            "keyword": None,
        }

    # ---------------------------------
    # ORDER IS IMPORTANT
    # ---------------------------------

    categories = [
        (
            "CRYPTO",
            CRYPTO_KEYWORDS,
        ),
        (
            "WEATHER",
            WEATHER_KEYWORDS,
        ),
        (
            "GOLD",
            GOLD_KEYWORDS,
        ),
        (
            "CURRENCY",
            CURRENCY_KEYWORDS,
        ),
        (
            "FUEL",
            FUEL_KEYWORDS,
        ),
        (
            "STOCK",
            STOCK_KEYWORDS,
        ),
        (
            "TRAIN",
            TRAIN_KEYWORDS,
        ),
        (
            "BUS",
            BUS_KEYWORDS,
        ),
        (
            "FLIGHT",
            FLIGHT_KEYWORDS,
        ),
        (
            "SPORTS",
            SPORTS_KEYWORDS,
        ),
        (
            "NEWS",
            NEWS_KEYWORDS,
        ),
        (
            "HOLIDAY",
            HOLIDAY_KEYWORDS,
        ),
        (
            "MOVIE",
            MOVIE_KEYWORDS,
        ),
        (
            "WIKIPEDIA",
            WIKIPEDIA_KEYWORDS,
        ),
        (
            "YOUTUBE",
            YOUTUBE_KEYWORDS,
        ),
        (
            "UNIT",
            UNIT_KEYWORDS,
        ),
    ]

    for (
        category,
        keywords,
    ) in categories:

        keyword = find_keyword(
            text,
            keywords,
        )

        if keyword:
            return {
                "live": True,
                "category": category,
                "keyword": keyword,
            }

    calculator_keyword = find_keyword(
        text,
        CALCULATOR_KEYWORDS,
    )

    if (
        calculator_keyword
        or looks_like_calculation(text)
    ):
        return {
            "live": True,
            "category": "CALCULATOR",
            "keyword": (
                calculator_keyword
                or "calculation"
            ),
        }

    return {
        "live": False,
        "category": "GENERAL",
        "keyword": None,
    }