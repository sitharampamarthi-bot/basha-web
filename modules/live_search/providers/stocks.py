from __future__ import annotations

import re
from datetime import datetime
from typing import Any

import requests
import yfinance as yf


YAHOO_SEARCH_URL = (
    "https://query2.finance.yahoo.com/v1/finance/search"
)


# Common names కోసం fast and accurate mapping.
# Unknown companies Yahoo Search ద్వారా resolve అవుతాయి.
KNOWN_INDIAN_SYMBOLS = {
    # Indices
    "nifty": "^NSEI",
    "nifty 50": "^NSEI",
    "నిఫ్టీ": "^NSEI",

    "bank nifty": "^NSEBANK",
    "banknifty": "^NSEBANK",
    "nifty bank": "^NSEBANK",
    "బ్యాంక్ నిఫ్టీ": "^NSEBANK",

    "sensex": "^BSESN",
    "bse sensex": "^BSESN",
    "సెన్సెక్స్": "^BSESN",

    # Popular Indian shares
    "reliance": "RELIANCE.NS",
    "reliance industries": "RELIANCE.NS",
    "రిలయన్స్": "RELIANCE.NS",

    "tcs": "TCS.NS",
    "tata consultancy services": "TCS.NS",

    "infosys": "INFY.NS",
    "infy": "INFY.NS",
    "ఇన్ఫోసిస్": "INFY.NS",

    "hdfc bank": "HDFCBANK.NS",
    "hdfc": "HDFCBANK.NS",

    "icici bank": "ICICIBANK.NS",
    "sbi": "SBIN.NS",
    "state bank of india": "SBIN.NS",

    "itc": "ITC.NS",
    "wipro": "WIPRO.NS",
    "axis bank": "AXISBANK.NS",
    "kotak bank": "KOTAKBANK.NS",

    "bharti airtel": "BHARTIARTL.NS",
    "airtel": "BHARTIARTL.NS",

    "tata motors": "TATAMOTORS.NS",
    "tata steel": "TATASTEEL.NS",
    "tata power": "TATAPOWER.NS",
    "tata elxsi": "TATAELXSI.NS",

    "bajaj finance": "BAJFINANCE.NS",
    "bajaj finserv": "BAJAJFINSV.NS",

    "maruti": "MARUTI.NS",
    "maruti suzuki": "MARUTI.NS",

    "mahindra": "M&M.NS",
    "mahindra and mahindra": "M&M.NS",

    "larsen and toubro": "LT.NS",
    "l&t": "LT.NS",

    "hindustan unilever": "HINDUNILVR.NS",
    "hul": "HINDUNILVR.NS",

    "asian paints": "ASIANPAINT.NS",
    "sun pharma": "SUNPHARMA.NS",
    "dr reddy": "DRREDDY.NS",
    "cipla": "CIPLA.NS",

    "adani enterprises": "ADANIENT.NS",
    "adani ports": "ADANIPORTS.NS",
    "adani power": "ADANIPOWER.NS",
    "adani green": "ADANIGREEN.NS",

    "coal india": "COALINDIA.NS",
    "ongc": "ONGC.NS",
    "ntpc": "NTPC.NS",
    "power grid": "POWERGRID.NS",

    "jsw steel": "JSWSTEEL.NS",
    "hindalco": "HINDALCO.NS",

    "ultratech cement": "ULTRACEMCO.NS",
    "grasim": "GRASIM.NS",

    "tech mahindra": "TECHM.NS",
    "hcl tech": "HCLTECH.NS",
    "hcl technologies": "HCLTECH.NS",

    "indusind bank": "INDUSINDBK.NS",
    "bank of baroda": "BANKBARODA.NS",
    "canara bank": "CANBK.NS",
    "punjab national bank": "PNB.NS",
}


REMOVE_PHRASES = {
    # English
    "share price",
    "stock price",
    "current price",
    "live price",
    "today price",
    "market price",
    "share rate",
    "stock rate",
    "latest price",
    "price today",
    "price",
    "share",
    "stock",
    "equity",
    "company",
    "nse",
    "bse",
    "india",
    "indian market",
    "today",
    "current",
    "live",
    "latest",
    "now",
    "please",
    "tell me",
    "show me",
    "what is",
    "how much",
    "give me",
    "about",

    # Telugu
    "షేర్ ధర",
    "స్టాక్ ధర",
    "ప్రస్తుత ధర",
    "లైవ్ ధర",
    "ఈరోజు ధర",
    "మార్కెట్ ధర",
    "ధర ఎంత",
    "ధర",
    "షేర్",
    "స్టాక్",
    "కంపెనీ",
    "ఈరోజు",
    "ప్రస్తుతం",
    "లైవ్",
    "ఇప్పుడు",
    "కావాలి",
    "చెప్పు",
    "చెప్పండి",
    "గురించి",
    "ఎంత",
    "ఏంటి",
    "ఏమిటి",
    "నాకు",
    "లో",
}


def clean_text(value: Any) -> str:
    return str(value or "").strip()


def normalize_query(value: str) -> str:
    text = clean_text(value).casefold()

    text = re.sub(
        r"[?.,!;:'\"()\[\]{}]+",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    return text


def extract_company_name(question: str) -> str:
    """
    User question నుంచి share/price వంటి filler words తీసేసి
    probable company name మాత్రమే return చేస్తుంది.
    """

    cleaned = normalize_query(question)

    if not cleaned:
        return ""

    for phrase in sorted(
        REMOVE_PHRASES,
        key=len,
        reverse=True,
    ):
        cleaned = cleaned.replace(
            phrase.casefold(),
            " ",
        )

    cleaned = re.sub(
        r"\b(?:of|the|for|in|at|on|from|please)\b",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned,
    ).strip()

    return cleaned


def find_known_symbol(
    question: str,
    company_name: str,
) -> tuple[str | None, str | None]:

    normalized_question = normalize_query(
        question
    )

    normalized_company = normalize_query(
        company_name
    )

    # Longer names first.
    for name in sorted(
        KNOWN_INDIAN_SYMBOLS,
        key=len,
        reverse=True,
    ):
        normalized_name = name.casefold()

        if (
            normalized_name ==
            normalized_company
        ):
            return (
                KNOWN_INDIAN_SYMBOLS[name],
                name,
            )

        if (
            normalized_name in
            normalized_question
        ):
            return (
                KNOWN_INDIAN_SYMBOLS[name],
                name,
            )

    return None, None


def search_indian_symbol(
    company_name: str,
) -> dict[str, Any]:
    """
    Yahoo Finance Search ద్వారా NSE/BSE symbol కనుక్కుంటుంది.
    NSE result ఉంటే మొదట దానికే preference ఇస్తుంది.
    """

    company_name = clean_text(
        company_name
    )

    if not company_name:
        return {
            "success": False,
            "error": (
                "Please include an Indian company name."
            ),
        }

    try:
        response = requests.get(
            YAHOO_SEARCH_URL,
            params={
                "q": company_name,
                "quotesCount": 12,
                "newsCount": 0,
                "enableFuzzyQuery": "true",
                "quotesQueryId":
                    "tss_match_phrase_query",
            },
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "Chrome/124.0 Safari/537.36"
                ),
                "Accept": "application/json",
            },
            timeout=12,
        )

        response.raise_for_status()

        payload = response.json()

        quotes = payload.get(
            "quotes"
        ) or []

        candidates = []

        for quote in quotes:
            symbol = clean_text(
                quote.get("symbol")
            ).upper()

            quote_type = clean_text(
                quote.get("quoteType")
            ).upper()

            exchange = clean_text(
                quote.get("exchange")
            ).upper()

            short_name = clean_text(
                quote.get("shortname")
                or quote.get("longname")
                or quote.get("displayName")
            )

            if not symbol:
                continue

            is_indian_symbol = (
                symbol.endswith(".NS")
                or symbol.endswith(".BO")
                or symbol in {
                    "^NSEI",
                    "^NSEBANK",
                    "^BSESN",
                }
            )

            is_supported_type = (
                quote_type in {
                    "EQUITY",
                    "INDEX",
                    "ETF",
                }
                or exchange in {
                    "NSI",
                    "BSE",
                }
            )

            if (
                not is_indian_symbol
                or not is_supported_type
            ):
                continue

            score = 0

            if symbol.endswith(".NS"):
                score += 100

            if symbol.endswith(".BO"):
                score += 70

            if quote_type == "EQUITY":
                score += 30

            searchable_name = (
                f"{short_name} {symbol}"
            ).casefold()

            query_words = [
                word
                for word in
                company_name.casefold().split()
                if len(word) >= 2
            ]

            for word in query_words:
                if word in searchable_name:
                    score += 10

            candidates.append({
                "symbol": symbol,
                "name": (
                    short_name
                    or symbol
                ),
                "exchange": exchange,
                "quoteType": quote_type,
                "score": score,
            })

        if not candidates:
            return {
                "success": False,
                "error": (
                    "Indian NSE/BSE share not found "
                    f"for: {company_name}"
                ),
            }

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        best = candidates[0]

        return {
            "success": True,
            "symbol": best["symbol"],
            "name": best["name"],
            "exchange": best["exchange"],
            "quoteType": best["quoteType"],
        }

    except requests.RequestException as error:
        return {
            "success": False,
            "error": (
                "Stock symbol search failed: "
                f"{error}"
            ),
        }

    except (
        TypeError,
        ValueError,
        KeyError,
    ) as error:
        return {
            "success": False,
            "error": (
                "Invalid Yahoo search response: "
                f"{error}"
            ),
        }


def resolve_indian_symbol(
    question: str,
) -> dict[str, Any]:

    company_name = extract_company_name(
        question
    )

    known_symbol, known_name = (
        find_known_symbol(
            question,
            company_name,
        )
    )

    if known_symbol:
        return {
            "success": True,
            "symbol": known_symbol,
            "name": known_name,
            "resolvedBy": "local-map",
            "query": company_name,
        }

    return search_indian_symbol(
        company_name
    )


def safe_number(
    value: Any,
) -> float | int | None:

    if value is None:
        return None

    try:
        number = float(value)

        if number.is_integer():
            return int(number)

        return round(number, 2)

    except (
        TypeError,
        ValueError,
    ):
        return None


def get_stock_quote(
    question: str,
) -> dict[str, Any]:

    resolution = resolve_indian_symbol(
        question
    )

    if not resolution.get("success"):
        return resolution

    symbol = clean_text(
        resolution.get("symbol")
    ).upper()

    resolved_name = clean_text(
        resolution.get("name")
    )

    try:
        ticker = yf.Ticker(
            symbol
        )

        fast_info = {}

        try:
            fast_info = dict(
                ticker.fast_info
            )
        except Exception:
            fast_info = {}

        history = ticker.history(
            period="5d",
            interval="1d",
            auto_adjust=False,
        )

        if history.empty:
            return {
                "success": False,
                "symbol": symbol,
                "error": (
                    f"No market quote available for "
                    f"{resolved_name or symbol}"
                ),
            }

        latest_row = history.iloc[-1]

        previous_close = None

        if len(history) >= 2:
            previous_close = safe_number(
                history.iloc[-2].get(
                    "Close"
                )
            )

        if previous_close is None:
            previous_close = safe_number(
                fast_info.get(
                    "previous_close"
                )
            )

        price = safe_number(
            fast_info.get(
                "last_price"
            )
        )

        if price is None:
            price = safe_number(
                latest_row.get(
                    "Close"
                )
            )

        open_price = safe_number(
            latest_row.get(
                "Open"
            )
        )

        high = safe_number(
            latest_row.get(
                "High"
            )
        )

        low = safe_number(
            latest_row.get(
                "Low"
            )
        )

        volume = safe_number(
            latest_row.get(
                "Volume"
            )
        )

        change = None
        change_percent = None

        if (
            price is not None
            and previous_close not in {
                None,
                0,
            }
        ):
            change = round(
                float(price) -
                float(previous_close),
                2,
            )

            change_percent = round(
                (
                    change /
                    float(previous_close)
                ) * 100,
                2,
            )

        currency = (
            "INR"
            if (
                symbol.endswith(".NS")
                or symbol.endswith(".BO")
                or symbol.startswith("^")
            )
            else clean_text(
                fast_info.get("currency")
            ) or "INR"
        )

        name = resolved_name

        try:
            quote_info = ticker.info or {}

            name = clean_text(
                quote_info.get("longName")
                or quote_info.get(
                    "shortName"
                )
                or resolved_name
                or symbol
            )

            currency = clean_text(
                quote_info.get("currency")
                or currency
            )

        except Exception:
            name = (
                resolved_name
                or symbol
            )

        history_index = history.index[-1]

        try:
            market_time = (
                history_index.isoformat()
            )
        except Exception:
            market_time = datetime.now().isoformat()

        exchange = (
            "NSE"
            if symbol.endswith(".NS")
            else (
                "BSE"
                if symbol.endswith(".BO")
                else "INDEX"
            )
        )

        return {
            "success": True,
            "symbol": symbol,
            "name": name,
            "exchange": exchange,
            "currency": currency,
            "price": price,
            "previousClose": previous_close,
            "change": change,
            "changePercent": change_percent,
            "open": open_price,
            "high": high,
            "low": low,
            "volume": volume,
            "marketTime": market_time,
            "source": (
                "Yahoo Finance via yfinance"
            ),
            "delayedPossible": True,
            "resolvedBy": resolution.get(
                "resolvedBy",
                "yahoo-search",
            ),
            "searchQuery": resolution.get(
                "query"
            ),
        }

    except Exception as error:
        return {
            "success": False,
            "symbol": symbol,
            "name": resolved_name,
            "error": (
                "Unable to load stock quote: "
                f"{error}"
            ),
        }