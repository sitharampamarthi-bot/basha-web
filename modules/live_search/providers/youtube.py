from __future__ import annotations

import os
import re
from typing import Any

import requests


YOUTUBE_SEARCH_URL = (
    "https://www.googleapis.com/youtube/v3/search"
)


def clean_youtube_query(
    question: str,
) -> str:

    text = str(
        question or ""
    ).strip()


    phrases = {
        "youtube videos",
        "youtube video",
        "youtube search",
        "youtube",
        "video search",

        "యూట్యూబ్",
    }


    for phrase in sorted(
        phrases,
        key=len,
        reverse=True,
    ):

        text = re.sub(
            re.escape(
                phrase
            ),
            " ",
            text,
            flags=re.IGNORECASE,
        )


    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def search_youtube(
    question: str,
) -> dict[str, Any]:

    api_key = str(
        os.getenv(
            "YOUTUBE_API_KEY"
        )
        or ""
    ).strip()


    if not api_key:

        return {
            "success": False,

            "configurationRequired":
                True,

            "error": (
                "YOUTUBE_API_KEY "
                "is not configured."
            ),
        }


    query = clean_youtube_query(
        question
    )


    if not query:

        return {
            "success": False,
            "error": (
                "Please include "
                "a YouTube search topic."
            ),
        }


    try:

        response = requests.get(
            YOUTUBE_SEARCH_URL,

            params={
                "part":
                    "snippet",

                "q":
                    query,

                "type":
                    "video",

                "maxResults":
                    5,

                "key":
                    api_key,

                "regionCode":
                    "IN",

                "safeSearch":
                    "moderate",
            },

            timeout=12,
        )

        response.raise_for_status()

        payload = response.json()


        videos = []


        for item in (
            payload.get(
                "items"
            )
            or []
        ):

            video_id = (
                item.get(
                    "id"
                )
                or {}
            ).get(
                "videoId"
            )


            snippet = (
                item.get(
                    "snippet"
                )
                or {}
            )


            if not video_id:
                continue


            videos.append({
                "videoId":
                    video_id,

                "title":
                    snippet.get(
                        "title"
                    ),

                "channelTitle":
                    snippet.get(
                        "channelTitle"
                    ),

                "publishedAt":
                    snippet.get(
                        "publishedAt"
                    ),

                "description":
                    snippet.get(
                        "description"
                    ),

                "url":
                    (
                        "https://www.youtube.com/"
                        f"watch?v={video_id}"
                    ),
            })


        if not videos:

            return {
                "success": False,
                "query": query,
                "error": (
                    "No YouTube "
                    "videos found."
                ),
            }


        return {
            "success": True,

            "query":
                query,

            "videos":
                videos,

            "source":
                "YouTube Data API",
        }


    except (
        requests.RequestException,
        ValueError,
    ) as error:

        return {
            "success": False,
            "query": query,
            "error": (
                "YouTube search failed: "
                f"{error}"
            ),
        }