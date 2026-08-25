from __future__ import annotations

import os
import re
from typing import Any

import requests


TMDB_SEARCH_URL = (
    "https://api.themoviedb.org/3/search/movie"
)


def clean_movie_query(
    question: str,
) -> str:

    text = str(
        question or ""
    ).strip()


    phrases = {
        "movie details",
        "latest movie",
        "movie rating",
        "release date",
        "movies",
        "movie",
        "film",
        "cinema",

        "సినిమాలు",
        "సినిమా",
        "మూవీ",
        "రిలీజ్",
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


def search_movies(
    question: str,
) -> dict[str, Any]:

    token = str(
        os.getenv(
            "TMDB_BEARER_TOKEN"
        )
        or ""
    ).strip()


    if not token:

        return {
            "success": False,

            "configurationRequired":
                True,

            "error": (
                "TMDB_BEARER_TOKEN "
                "is not configured."
            ),
        }


    query = clean_movie_query(
        question
    )


    if not query:

        return {
            "success": False,
            "error": (
                "Please include "
                "a movie name."
            ),
        }


    try:

        response = requests.get(
            TMDB_SEARCH_URL,

            params={
                "query":
                    query,

                "include_adult":
                    "false",

                "language":
                    "en-US",

                "page":
                    1,
            },

            headers={
                "Authorization":
                    f"Bearer {token}",

                "Accept":
                    "application/json",
            },

            timeout=12,
        )

        response.raise_for_status()

        payload = response.json()


        movies = []


        for item in (
            payload.get(
                "results"
            )
            or []
        )[:5]:

            movies.append({
                "title":
                    item.get(
                        "title"
                    ),

                "originalTitle":
                    item.get(
                        "original_title"
                    ),

                "releaseDate":
                    item.get(
                        "release_date"
                    ),

                "rating":
                    item.get(
                        "vote_average"
                    ),

                "voteCount":
                    item.get(
                        "vote_count"
                    ),

                "overview":
                    item.get(
                        "overview"
                    ),

                "language":
                    item.get(
                        "original_language"
                    ),
            })


        if not movies:

            return {
                "success": False,
                "query": query,
                "error": (
                    "Movie not found."
                ),
            }


        return {
            "success": True,

            "query":
                query,

            "movies":
                movies,

            "source":
                "TMDB",
        }


    except (
        requests.RequestException,
        ValueError,
    ) as error:

        return {
            "success": False,
            "query": query,
            "error": (
                "Movie service failed: "
                f"{error}"
            ),
        }