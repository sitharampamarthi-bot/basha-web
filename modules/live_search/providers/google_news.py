from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from typing import Any

import requests


GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search"
)


REMOVE_WORDS = {
    "latest news",
    "today news",
    "breaking news",
    "breaking",
    "headlines",
    "news",

    "తాజా వార్తలు",
    "వార్తలు",
    "న్యూస్",
}


def clean_news_query(
    question: str,
) -> str:

    text = str(
        question or ""
    ).strip()

    for word in sorted(
        REMOVE_WORDS,
        key=len,
        reverse=True,
    ):

        text = re.sub(
            re.escape(word),
            " ",
            text,
            flags=re.IGNORECASE,
        )

    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    return text or "India"


def get_news(
    question: str,
) -> dict[str, Any]:

    query = clean_news_query(
        question
    )

    try:

        response = requests.get(
            GOOGLE_NEWS_RSS,

            params={
                "q": query,
                "hl": "en-IN",
                "gl": "IN",
                "ceid": "IN:en",
            },

            headers={
                "User-Agent":
                    "Basha-Messenger/1.0",
            },

            timeout=12,
        )

        response.raise_for_status()

        root = ET.fromstring(
            response.content
        )


        results = []


        for item in root.findall(
            ".//item"
        )[:10]:

            title = html.unescape(
                item.findtext(
                    "title"
                )
                or ""
            ).strip()

            link = (
                item.findtext(
                    "link"
                )
                or ""
            ).strip()

            published = (
                item.findtext(
                    "pubDate"
                )
                or ""
            ).strip()


            source_node = (
                item.find("source")
            )

            source = ""

            if (
                source_node is not None
                and source_node.text
            ):
                source = (
                    source_node.text
                    .strip()
                )


            if not title:
                continue


            results.append({
                "title":
                    title,

                "source":
                    source,

                "published":
                    published,

                "link":
                    link,
            })


        if not results:

            return {
                "success": False,
                "query": query,
                "error": (
                    "No recent news results "
                    "were returned."
                ),
            }


        return {
            "success": True,

            "query":
                query,

            "items":
                results,

            "source":
                "Google News RSS",
        }


    except (
        requests.RequestException,
        ET.ParseError,
    ) as error:

        return {
            "success": False,
            "query": query,
            "error": (
                "News service failed: "
                f"{error}"
            ),
        }