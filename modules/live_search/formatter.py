from typing import Any


def value_or_unknown(
    value: Any,
    suffix: str = "",
) -> str:
    if value is None:
        return "Unknown"

    return f"{value}{suffix}"


def format_crypto(
    data: dict[str, Any],
) -> str | None:
    if not data.get("success"):
        return None

    return f"""
VERIFIED LIVE CRYPTOCURRENCY DATA

Asset: {data.get('coin')}

Current price in US dollars:
${data.get('usd')}

Current price in Indian rupees:
₹{data.get('inr', 0):,}

Change during the last 24 hours:
{data.get('change24h')} percent

Data provider:
CoinGecko

Instructions:
Use these current values exactly.
Explain the price and 24-hour movement naturally.
Do not invent additional current prices.
""".strip()


def format_weather(
    data: dict[str, Any],
) -> str | None:
    if not data.get("success"):
        return None

    forecast = data.get("forecast") or []

    forecast_lines = []

    for index, day in enumerate(
        forecast
    ):
        label = (
            "Today"
            if index == 0
            else (
                "Tomorrow"
                if index == 1
                else f"Day {index + 1}"
            )
        )

        forecast_lines.append(
            f"""
{label}:
Date: {day.get('date')}
Condition: {day.get('condition')}
Maximum temperature: {
    value_or_unknown(
        day.get('maximumTemperature'),
        ' degrees Celsius'
    )
}
Minimum temperature: {
    value_or_unknown(
        day.get('minimumTemperature'),
        ' degrees Celsius'
    )
}
Maximum rain probability: {
    value_or_unknown(
        day.get('rainProbability'),
        ' percent'
    )
}
Sunrise: {value_or_unknown(day.get('sunrise'))}
Sunset: {value_or_unknown(day.get('sunset'))}
""".strip()
        )

    forecast_text = "\n\n".join(
        forecast_lines
    )

    location_parts = [
        data.get("location"),
        data.get("region"),
        data.get("country"),
    ]

    location_name = ", ".join(
        str(item)
        for item in location_parts
        if item
    )

    return f"""
VERIFIED LIVE WEATHER DATA

Location:
{location_name}

Observation time:
{value_or_unknown(data.get('observationTime'))}

Current condition:
{value_or_unknown(data.get('condition'))}

Current temperature:
{
    value_or_unknown(
        data.get('temperature'),
        ' degrees Celsius'
    )
}

Feels like:
{
    value_or_unknown(
        data.get('feelsLike'),
        ' degrees Celsius'
    )
}

Relative humidity:
{
    value_or_unknown(
        data.get('humidity'),
        ' percent'
    )
}

Current precipitation:
{
    value_or_unknown(
        data.get('precipitation'),
        ' millimetres'
    )
}

Current rain:
{
    value_or_unknown(
        data.get('rain'),
        ' millimetres'
    )
}

Cloud cover:
{
    value_or_unknown(
        data.get('cloudCover'),
        ' percent'
    )
}

Wind speed:
{
    value_or_unknown(
        data.get('windSpeed'),
        ' kilometres per hour'
    )
}

Wind direction:
{
    value_or_unknown(
        data.get('windDirection'),
        ' degrees'
    )
}

FORECAST

{forecast_text}

Data provider:
Open-Meteo

Instructions:
Use these live weather values exactly.
Answer in the user's preferred language.
Clearly separate current conditions from forecast.
If the user asks about rain, explain the rain probability.
Do not invent weather alerts or measurements.
""".strip()

def format_stock(
    data: dict[str, Any],
) -> str | None:
    if not data.get("success"):
        return None

    currency = data.get(
        "currency",
        ""
    )

    currency_symbol = (
        "₹"
        if currency == "INR"
        else "$"
    )

    change = data.get("change")
    change_percent = data.get(
        "changePercent"
    )

    movement = "unchanged"

    if (
        change_percent is not None
        and change_percent > 0
    ):
        movement = "up"

    elif (
        change_percent is not None
        and change_percent < 0
    ):
        movement = "down"

    return f"""
VERIFIED MARKET QUOTE DATA

Instrument:
{data.get('name')}

Ticker symbol:
{data.get('symbol')}

Currency:
{currency}

Latest available price:
{currency_symbol}{data.get('price')}

Previous close:
{currency_symbol}{data.get('previousClose')}

Absolute change:
{data.get('change')}

Percentage change:
{data.get('changePercent')} percent

Market direction:
{movement}

Session open:
{currency_symbol}{data.get('open')}

Session high:
{currency_symbol}{data.get('high')}

Session low:
{currency_symbol}{data.get('low')}

Volume:
{data.get('volume')}

Market data time:
{data.get('marketTime')}

Data provider:
{data.get('source')}

Important:
This quote may be delayed.

Instructions:
Use these supplied market values exactly.
Explain whether the instrument moved up or down.
Do not invent intraday prices, support, resistance,
targets, predictions or trading recommendations.
Clearly mention that market quotes may be delayed.
Answer in the user's preferred language.
""".strip()

def format_live_result(
    result: dict[str, Any],
) -> str | None:
    if not result.get("live"):
        return None

    category = result.get("category")
    data = result.get("data")

    if not isinstance(data, dict):
        return None

    if category == "CRYPTO":
        return format_crypto(data)

    if category == "WEATHER":
        return format_weather(data)

    if category == "STOCK":
        return format_stock(data)

    return None