from __future__ import annotations

import re
from typing import Any

import requests


WIKIPEDIA_API = (
    "https://en.wikipedia.org/w/api.php"
)


def clean_wikipedia_query(
    question: str,
) -> str:

    text = str(
        question or ""
    ).strip()


    text = re.sub(
        r"\b(?:wikipedia|wiki)\b",
        " ",
        text,
        flags=re.IGNORECASE,
    )


    text = (
        text
        .replace(
            "వికీపీడియా",
            " ",
        )
        .replace(
            "వికీ",
            " ",
        )
    )


    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def search_wikipedia(
    question: str,
) -> dict[str, Any]:

    query = clean_wikipedia_query(
        question
    )


    if not query:

        return {
            "success": False,
            "error": (
                "Please include "
                "a Wikipedia topic."
            ),
        }


    try:

        response = requests.get(
            WIKIPEDIA_API,

            params={
                "action":
                    "query",

                "list":
                    "search",

                "srsearch":
                    query,

                "utf8":
                    1,

                "format":
                    "json",

                "srlimit":
                    5,
            },

            headers={
                "User-Agent":
                    "Basha-Messenger/1.0",
            },

            timeout=10,
        )

        response.raise_for_status()

        payload = response.json()


        results = []


        for item in (
            payload
            .get(
                "query",
                {},
            )
            .get(
                "search",
                [],
            )
        ):

            snippet = re.sub(
                r"<[^>]+>",
                "",
                item.get(
                    "snippet"
                )
                or "",
            )


            results.append({
                "title":
                    item.get(
                        "title"
                    ),

                "snippet":
                    snippet,

                "pageId":
                    item.get(
                        "pageid"
                    ),
            })


        if not results:

            return {
                "success": False,
                "query": query,
                "error": (
                    "Wikipedia topic "
                    "not found."
                ),
            }


        return {
            "success": True,

            "query":
                query,

            "results":
                results,

            "source":
                "Wikipedia",
        }


    except (
        requests.RequestException,
        ValueError,
    ) as error:

        return {
            "success": False,
            "query": query,
            "error": (
                "Wikipedia search failed: "
                f"{error}"
            ),
        }