from __future__ import annotations

import re
from datetime import datetime
from typing import Any

import requests


NAGER_BASE_URL = "https://date.nager.at/api/v3/PublicHolidays"


COUNTRY_ALIASES = {
    "india": "IN",
    "indian": "IN",
    "bharat": "IN",
    "భారత్": "IN",
    "భారతదేశం": "IN",
    "ఇండియా": "IN",

    "usa": "US",
    "united states": "US",
    "america": "US",

    "uk": "GB",
    "united kingdom": "GB",
    "britain": "GB",

    "canada": "CA",
    "australia": "AU",
    "germany": "DE",
    "france": "FR",
    "japan": "JP",
    "singapore": "SG",
}


def detect_country(
    question: str,
) -> str:

    text = str(
        question or ""
    ).casefold()

    for alias, code in sorted(
        COUNTRY_ALIASES.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        if alias.casefold() in text:
            return code

    return "IN"


def detect_year(
    question: str,
) -> int:

    match = re.search(
        r"\b(20\d{2})\b",
        str(question or ""),
    )

    if match:
        return int(
            match.group(1)
        )

    return datetime.now().year


def normalize_holiday(
    item: dict[str, Any],
) -> dict[str, Any]:

    return {
        "date": item.get("date"),
        "localName": item.get("localName"),
        "name": item.get("name"),
        "countryCode": item.get("countryCode"),
        "fixed": item.get("fixed"),
        "global": item.get("global"),
        "counties": item.get("counties") or [],
        "launchYear": item.get("launchYear"),
        "types": item.get("types") or [],
    }


def get_holidays(
    question: str,
) -> dict[str, Any]:

    country = detect_country(
        question
    )

    year = detect_year(
        question
    )

    url = (
        f"{NAGER_BASE_URL}/"
        f"{year}/"
        f"{country}"
    )

    try:

        response = requests.get(
            url,
            headers={
                "User-Agent":
                    "Mozilla/5.0 "
                    "(compatible; "
                    "BashaMessenger/1.0)",

                "Accept":
                    "application/json",
            },
            timeout=15,
        )

        if response.status_code != 200:

            return {
                "success": False,
                "countryCode": country,
                "year": year,
                "statusCode":
                    response.status_code,
                "error": (
                    "Holiday provider returned "
                    f"HTTP {response.status_code}."
                ),
                "source": "Nager.Date",
            }

        content_type = (
            response.headers.get(
                "Content-Type",
                "",
            )
            .casefold()
        )

        raw_text = (
            response.text or ""
        ).strip()

        if not raw_text:

            return {
                "success": False,
                "countryCode": country,
                "year": year,
                "error": (
                    "Holiday provider returned "
                    "an empty response."
                ),
                "source": "Nager.Date",
            }

        if (
            "json" not in content_type
            and
            not raw_text.startswith("[")
            and
            not raw_text.startswith("{")
        ):

            return {
                "success": False,
                "countryCode": country,
                "year": year,
                "error": (
                    "Holiday provider returned "
                    "a non-JSON response."
                ),
                "source": "Nager.Date",
            }

        try:
            payload = response.json()

        except ValueError:

            return {
                "success": False,
                "countryCode": country,
                "year": year,
                "error": (
                    "Holiday provider returned "
                    "invalid JSON."
                ),
                "source": "Nager.Date",
            }

        if not isinstance(
            payload,
            list,
        ):

            return {
                "success": False,
                "countryCode": country,
                "year": year,
                "error": (
                    "Unexpected holiday "
                    "provider response."
                ),
                "source": "Nager.Date",
            }

        holidays = []

        for item in payload:

            if not isinstance(
                item,
                dict,
            ):
                continue

            holidays.append(
                normalize_holiday(
                    item
                )
            )

        if not holidays:

            return {
                "success": False,
                "countryCode": country,
                "year": year,
                "error": (
                    "No public holiday data "
                    "was returned for this "
                    "country and year."
                ),
                "source": "Nager.Date",
            }

        holidays.sort(
            key=lambda item:
                str(
                    item.get("date")
                    or ""
                )
        )

        return {
            "success": True,
            "countryCode": country,
            "year": year,
            "holidays": holidays,
            "count": len(holidays),
            "source": "Nager.Date",
        }

    except requests.Timeout:

        return {
            "success": False,
            "countryCode": country,
            "year": year,
            "error": (
                "Holiday provider "
                "request timed out."
            ),
            "source": "Nager.Date",
        }

    except requests.RequestException as error:

        return {
            "success": False,
            "countryCode": country,
            "year": year,
            "error": (
                "Holiday provider "
                "request failed: "
                f"{error}"
            ),
            "source": "Nager.Date",
        }

    except Exception as error:

        return {
            "success": False,
            "countryCode": country,
            "year": year,
            "error": (
                "Holiday provider failed: "
                f"{error}"
            ),
            "source": "Nager.Date",
        }