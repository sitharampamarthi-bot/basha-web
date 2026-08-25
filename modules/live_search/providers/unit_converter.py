from __future__ import annotations

import re
from typing import Any


ALIASES = {
    "km": "km",
    "kilometer": "km",
    "kilometers": "km",
    "kilometre": "km",
    "kilometres": "km",

    "m": "m",
    "meter": "m",
    "meters": "m",
    "metre": "m",
    "metres": "m",

    "cm": "cm",
    "centimeter": "cm",
    "centimeters": "cm",

    "mm": "mm",
    "millimeter": "mm",
    "millimeters": "mm",

    "mi": "mi",
    "mile": "mi",
    "miles": "mi",

    "ft": "ft",
    "foot": "ft",
    "feet": "ft",

    "in": "in",
    "inch": "in",
    "inches": "in",

    "kg": "kg",
    "kilogram": "kg",
    "kilograms": "kg",

    "g": "g",
    "gram": "g",
    "grams": "g",

    "lb": "lb",
    "lbs": "lb",
    "pound": "lb",
    "pounds": "lb",

    "l": "l",
    "liter": "l",
    "liters": "l",
    "litre": "l",
    "litres": "l",

    "ml": "ml",
    "milliliter": "ml",
    "milliliters": "ml",
    "millilitre": "ml",

    "c": "c",
    "celsius": "c",

    "f": "f",
    "fahrenheit": "f",
}


TO_BASE = {
    "km":
        ("length", 1000.0),

    "m":
        ("length", 1.0),

    "cm":
        ("length", 0.01),

    "mm":
        ("length", 0.001),

    "mi":
        ("length", 1609.344),

    "ft":
        ("length", 0.3048),

    "in":
        ("length", 0.0254),

    "kg":
        ("mass", 1.0),

    "g":
        ("mass", 0.001),

    "lb":
        ("mass", 0.45359237),

    "l":
        ("volume", 1.0),

    "ml":
        ("volume", 0.001),
}


def normalize_unit(
    value: str,
) -> str | None:

    return ALIASES.get(
        str(
            value or ""
        )
        .casefold()
        .strip()
    )


def convert_units(
    question: str,
) -> dict[str, Any]:

    text = str(
        question or ""
    ).casefold()


    text = re.sub(
        r"\b(?:convert|conversion)\b",
        " ",
        text,
        flags=re.IGNORECASE,
    )


    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


    match = re.search(
        (
            r"(-?\d+(?:\.\d+)?)"
            r"\s*([a-z]+)"
            r"\s+(?:to|in)"
            r"\s+([a-z]+)"
        ),
        text,
        flags=re.IGNORECASE,
    )


    if not match:

        return {
            "success": False,
            "error": (
                "Use format like "
                "'5 km to miles' or "
                "'32 celsius to fahrenheit'."
            ),
        }


    value = float(
        match.group(1)
    )


    source = normalize_unit(
        match.group(2)
    )


    target = normalize_unit(
        match.group(3)
    )


    if not source or not target:

        return {
            "success": False,
            "error": (
                "Unsupported unit."
            ),
        }


    if (
        source in {"c", "f"}
        or
        target in {"c", "f"}
    ):

        if {
            source,
            target,
        } != {"c", "f"}:

            return {
                "success": False,
                "error": (
                    "Temperature conversion "
                    "supports Celsius and "
                    "Fahrenheit only."
                ),
            }


        if source == "c":

            result = (
                value * 9 / 5
                + 32
            )

        else:

            result = (
                value - 32
            ) * 5 / 9


    else:

        source_type, source_factor = (
            TO_BASE[source]
        )

        target_type, target_factor = (
            TO_BASE[target]
        )


        if source_type != target_type:

            return {
                "success": False,
                "error": (
                    "Those units measure "
                    "different quantities."
                ),
            }


        result = (
            value
            * source_factor
            / target_factor
        )


    return {
        "success": True,

        "value":
            value,

        "fromUnit":
            source,

        "toUnit":
            target,

        "result":
            round(
                result,
                8,
            ),

        "source":
            "Local unit converter",
    }