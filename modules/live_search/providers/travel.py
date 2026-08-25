from __future__ import annotations

import re
from typing import Any


def extract_route(
    question: str,
) -> tuple[
    str,
    str,
]:

    text = str(
        question or ""
    ).strip()


    english_match = re.search(
        (
            r"from\s+(.+?)\s+to\s+"
            r"(.+?)(?:\s+"
            r"(?:train|bus|flight|"
            r"ticket|booking).*)?$"
        ),
        text,
        flags=re.IGNORECASE,
    )


    if english_match:

        return (
            english_match
            .group(1)
            .strip(),

            english_match
            .group(2)
            .strip(),
        )


    telugu_match = re.search(
        (
            r"(.+?)\s+నుంచి\s+"
            r"(.+?)\s+"
            r"(?:వరకు|కి)"
        ),
        text,
    )


    if telugu_match:

        return (
            telugu_match
            .group(1)
            .strip(),

            telugu_match
            .group(2)
            .strip(),
        )


    return "", ""


def get_travel_handoff(
    question: str,
    mode: str,
) -> dict[str, Any]:

    origin, destination = (
        extract_route(
            question
        )
    )


    mode = str(
        mode or ""
    ).upper()


    booking_links = {
        "TRAIN":
            "https://www.irctc.co.in/",

        "BUS":
            "https://www.redbus.in/",

        "FLIGHT":
            "https://www.google.com/travel/flights",
    }


    return {
        "success": True,

        "mode":
            mode,

        "origin":
            origin,

        "destination":
            destination,

        "transactionalBooking":
            False,

        "bookingLink":
            booking_links.get(
                mode
            ),

        "message": (
            "Search handoff is available. "
            "Actual availability, fare, "
            "passenger details, payment "
            "and ticket confirmation must "
            "be completed through the "
            "booking provider."
        ),

        "source":
            "Booking handoff",
    }


def get_train(
    question: str,
) -> dict[str, Any]:

    return get_travel_handoff(
        question,
        "TRAIN",
    )


def get_bus(
    question: str,
) -> dict[str, Any]:

    return get_travel_handoff(
        question,
        "BUS",
    )


def get_flight(
    question: str,
) -> dict[str, Any]:

    return get_travel_handoff(
        question,
        "FLIGHT",
    )