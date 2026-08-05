import re
from typing import Any

import requests


GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

FORECAST_URL = (
    "https://api.open-meteo.com/v1/forecast"
)


WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Light snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Light rain showers",
    81: "Moderate rain showers",
    82: "Heavy rain showers",
    85: "Light snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with light hail",
    99: "Thunderstorm with heavy hail",
}


WEATHER_WORDS = {
    "weather",
    "temperature",
    "forecast",
    "rain",
    "humidity",
    "wind",
    "climate",
    "weather today",
    "weather tomorrow",
    "today weather",
    "tomorrow weather",
    "current weather",
    "weather now",
    "today",
    "tomorrow",
    "now",
    "current",
    "currently",

    "వాతావరణం",
    "ఉష్ణోగ్రత",
    "వర్షం",
    "వాన",
    "హ్యూమిడిటీ",
    "గాలి",
    "వెదర్",
    "టెంపరేచర్",
    "ఫోర్‌కాస్ట్",
    "ఈరోజు",
    "రేపు",
    "ఇప్పుడు",
    "నేడు",
}


TELUGU_LOCATION_MAP = {
    "హైదరాబాద్": "Hyderabad",
    "హైదరాబాదు": "Hyderabad",
    "విజయవాడ": "Vijayawada",
    "విశాఖపట్నం": "Visakhapatnam",
    "వైజాగ్": "Visakhapatnam",
    "చెన్నై": "Chennai",
    "బెంగళూరు": "Bengaluru",
    "బెంగుళూరు": "Bengaluru",
    "ముంబై": "Mumbai",
    "ఢిల్లీ": "Delhi",
    "న్యూఢిల్లీ": "New Delhi",
    "కోల్‌కతా": "Kolkata",
    "పుణే": "Pune",
    "తిరుపతి": "Tirupati",
    "గుంటూరు": "Guntur",
    "నెల్లూరు": "Nellore",
    "కర్నూలు": "Kurnool",
    "వరంగల్": "Warangal",
    "ఖమ్మం": "Khammam",
    "రాజమండ్రి": "Rajahmundry",
    "కాకినాడ": "Kakinada",
}


def clean_text(value: Any) -> str:
    return str(value or "").strip()


def translate_telugu_location(
    location: str,
) -> str:
    cleaned_location = clean_text(
        location
    )

    if not cleaned_location:
        return ""

    direct_match = (
        TELUGU_LOCATION_MAP.get(
            cleaned_location
        )
    )

    if direct_match:
        return direct_match

    for telugu_name, english_name in (
        TELUGU_LOCATION_MAP.items()
    ):
        if telugu_name in cleaned_location:
            return english_name

    return cleaned_location


def extract_location(
    question: str,
) -> str:
    """
    Weather, time and filler words తొలగించి
    probable location మాత్రమే return చేస్తుంది.
    """

    text = clean_text(
        question
    )

    if not text:
        return ""

    cleaned = text.casefold()

    removable_phrases = sorted(
        WEATHER_WORDS.union({
            "వాతావరణం ఎలా ఉంది",
            "వాతావరణం ఎలా ఉంటుంది",
            "వర్షం పడుతుందా",
            "వాన పడుతుందా",
            "వర్షం పడుతుందా చెప్పు",
            "వాన పడుతుందా చెప్పు",
            "ఎలా ఉంది",
            "ఎలా ఉంటుంది",
            "చెప్పు",
            "చెప్పండి",
            "కావాలి",
            "తెలియజేయి",
            "తెలియజేయండి",
        }),
        key=len,
        reverse=True,
    )

    for phrase in removable_phrases:
        cleaned = cleaned.replace(
            phrase.casefold(),
            " ",
        )

    cleaned = re.sub(
        r"\b(?:in|at|near|for|of|the|please|show|tell|me)\b",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"(గురించి|ఎంత|ఉందా|ఉంది|ఉంటుంది|పడుతుంది|పడుతుందా)",
        " ",
        cleaned,
    )

    cleaned = re.sub(
        r"[?.,!;:'\"()\[\]{}]+",
        " ",
        cleaned,
    )

    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned,
    ).strip()

    telugu_suffixes = (
        "లోని",
        "వద్ద",
        "దగ్గర",
        "నుంచి",
        "లో",
        "కి",
    )

    for suffix in telugu_suffixes:
        if cleaned.endswith(suffix):
            cleaned = cleaned[
                :-len(suffix)
            ].strip()
            break

    cleaned = re.sub(
        r"\s+(లోని|వద్ద|దగ్గర|నుంచి|లో|కి)\s+",
        " ",
        cleaned,
    )

    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned,
    ).strip()

    cleaned = translate_telugu_location(
        cleaned
    )

    return cleaned


def geocode_location(
    location: str,
) -> dict[str, Any]:
    try:
        response = requests.get(
            GEOCODING_URL,
            params={
                "name": location,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=10,
        )

        response.raise_for_status()

        payload = response.json()

        results = (
            payload.get("results")
            or []
        )

        if not results:
            return {
                "success": False,
                "error": (
                    f"Location not found: "
                    f"{location}"
                ),
            }

        place = results[0]

        return {
            "success": True,
            "name": place.get("name"),
            "admin1": place.get("admin1"),
            "country": place.get("country"),
            "latitude": place.get(
                "latitude"
            ),
            "longitude": place.get(
                "longitude"
            ),
            "timezone": place.get(
                "timezone",
                "auto",
            ),
        }

    except requests.RequestException as error:
        return {
            "success": False,
            "error": (
                "Weather location service failed: "
                f"{error}"
            ),
        }

    except (
        TypeError,
        ValueError,
    ) as error:
        return {
            "success": False,
            "error": (
                "Invalid location response: "
                f"{error}"
            ),
        }


def get_weather(
    question: str,
) -> dict[str, Any]:
    location = extract_location(
        question
    )

    print(
        "WEATHER QUESTION:",
        question
    )

    print(
        "EXTRACTED LOCATION:",
        location
    )

    if not location:
        return {
            "success": False,
            "error": (
                "Please include a city "
                "or location."
            ),
        }

    place = geocode_location(
        location
    )

    if not place.get("success"):
        return place

    try:
        response = requests.get(
            FORECAST_URL,
            params={
                "latitude":
                    place["latitude"],

                "longitude":
                    place["longitude"],

                "timezone":
                    "auto",

                "current":
                    ",".join([
                        "temperature_2m",
                        "apparent_temperature",
                        "relative_humidity_2m",
                        "precipitation",
                        "rain",
                        "weather_code",
                        "cloud_cover",
                        "wind_speed_10m",
                        "wind_direction_10m",
                    ]),

                "daily":
                    ",".join([
                        "weather_code",
                        "temperature_2m_max",
                        "temperature_2m_min",
                        "precipitation_probability_max",
                        "sunrise",
                        "sunset",
                    ]),

                "forecast_days":
                    3,
            },
            timeout=12,
        )

        response.raise_for_status()

        payload = response.json()

        current = (
            payload.get("current")
            or {}
        )

        daily = (
            payload.get("daily")
            or {}
        )

        current_code = current.get(
            "weather_code"
        )

        daily_codes = (
            daily.get("weather_code")
            or []
        )

        dates = (
            daily.get("time")
            or []
        )

        maximums = (
            daily.get(
                "temperature_2m_max"
            )
            or []
        )

        minimums = (
            daily.get(
                "temperature_2m_min"
            )
            or []
        )

        rain_probabilities = (
            daily.get(
                "precipitation_probability_max"
            )
            or []
        )

        sunrises = (
            daily.get("sunrise")
            or []
        )

        sunsets = (
            daily.get("sunset")
            or []
        )

        forecast = []

        for index, date_value in enumerate(
            dates[:3]
        ):
            code = (
                daily_codes[index]
                if index < len(
                    daily_codes
                )
                else None
            )

            forecast.append({
                "date":
                    date_value,

                "condition":
                    WEATHER_CODES.get(
                        code,
                        "Unknown",
                    ),

                "maximumTemperature": (
                    maximums[index]
                    if index < len(
                        maximums
                    )
                    else None
                ),

                "minimumTemperature": (
                    minimums[index]
                    if index < len(
                        minimums
                    )
                    else None
                ),

                "rainProbability": (
                    rain_probabilities[index]
                    if index < len(
                        rain_probabilities
                    )
                    else None
                ),

                "sunrise": (
                    sunrises[index]
                    if index < len(
                        sunrises
                    )
                    else None
                ),

                "sunset": (
                    sunsets[index]
                    if index < len(
                        sunsets
                    )
                    else None
                ),
            })

        return {
            "success":
                True,

            "location":
                place["name"],

            "region":
                place.get("admin1"),

            "country":
                place.get("country"),

            "latitude":
                place["latitude"],

            "longitude":
                place["longitude"],

            "timezone":
                payload.get("timezone"),

            "observationTime":
                current.get("time"),

            "temperature":
                current.get(
                    "temperature_2m"
                ),

            "feelsLike":
                current.get(
                    "apparent_temperature"
                ),

            "humidity":
                current.get(
                    "relative_humidity_2m"
                ),

            "precipitation":
                current.get(
                    "precipitation"
                ),

            "rain":
                current.get("rain"),

            "cloudCover":
                current.get(
                    "cloud_cover"
                ),

            "windSpeed":
                current.get(
                    "wind_speed_10m"
                ),

            "windDirection":
                current.get(
                    "wind_direction_10m"
                ),

            "weatherCode":
                current_code,

            "condition":
                WEATHER_CODES.get(
                    current_code,
                    "Unknown",
                ),

            "forecast":
                forecast,

            "source":
                "Open-Meteo",
        }

    except requests.RequestException as error:
        return {
            "success": False,
            "error": (
                "Weather service failed: "
                f"{error}"
            ),
        }

    except (
        TypeError,
        ValueError,
    ) as error:
        return {
            "success": False,
            "error": (
                "Invalid weather response: "
                f"{error}"
            ),
        }