from __future__ import annotations

import re
from typing import Any

CRYPTO_KEYWORDS = [
    "bitcoin",
    "btc",
    "ethereum",
    "eth",
    "solana",
    "dogecoin",
    "bnb",
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

STOCK_KEYWORDS = [
    # Indices
    "bank nifty",
    "banknifty",
    "nifty bank",
    "nifty 50",
    "nifty",
    "sensex",
    "బ్యాంక్ నిఫ్టీ",
    "నిఫ్టీ",
    "సెన్సెక్స్",

    # Generic stock intent
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

    # Telugu generic intent
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
    "breaking",
    "వార్తలు",
    "న్యూస్",
]

SPORTS_KEYWORDS = [
    "live score",
    "ipl",
    "cricket",
    "football",
    "match score",
    "క్రికెట్",
    "ఐపీఎల్",
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
    "dollar rate",
    "currency rate",
    "exchange rate",
    "usd",
    "inr",
    "dollar",
    "rupee",
    "currency",
    "డాలర్ ధర",
    "డాలర్",
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

    q = normalize_text(
        question
    )

    word = normalize_text(
        keyword
    )

    if not q or not word:
        return False

    # English/number textలో complete phrase matching.
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

    # Telugu and other scripts.
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

    # IMPORTANT:
    # Cryptoని stockకంటే ముందుగా check చేయాలి.
    # లేకపోతే bitcoinలో "itc" వంటి చిన్న stock words
    # accidentalగా match కావచ్చు.
    crypto_keyword = find_keyword(
        text,
        CRYPTO_KEYWORDS,
    )

    if crypto_keyword:
        return {
            "live": True,
            "category": "CRYPTO",
            "keyword": crypto_keyword,
        }

    weather_keyword = find_keyword(
        text,
        WEATHER_KEYWORDS,
    )

    if weather_keyword:
        return {
            "live": True,
            "category": "WEATHER",
            "keyword": weather_keyword,
        }

    stock_keyword = find_keyword(
        text,
        STOCK_KEYWORDS,
    )

    if stock_keyword:
        return {
            "live": True,
            "category": "STOCK",
            "keyword": stock_keyword,
        }

    gold_keyword = find_keyword(
        text,
        GOLD_KEYWORDS,
    )

    if gold_keyword:
        return {
            "live": True,
            "category": "GOLD",
            "keyword": gold_keyword,
        }

    currency_keyword = find_keyword(
        text,
        CURRENCY_KEYWORDS,
    )

    if currency_keyword:
        return {
            "live": True,
            "category": "CURRENCY",
            "keyword": currency_keyword,
        }

    sports_keyword = find_keyword(
        text,
        SPORTS_KEYWORDS,
    )

    if sports_keyword:
        return {
            "live": True,
            "category": "SPORTS",
            "keyword": sports_keyword,
        }

    news_keyword = find_keyword(
        text,
        NEWS_KEYWORDS,
    )

    if news_keyword:
        return {
            "live": True,
            "category": "NEWS",
            "keyword": news_keyword,
        }

    return {
        "live": False,
        "category": "GENERAL",
        "keyword": None,
    }