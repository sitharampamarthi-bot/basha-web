from __future__ import annotations

from typing import Any


def value_or_unknown(
    value: Any,
    suffix: str = "",
) -> str:

    if value is None:
        return "Unknown"

    return f"{value}{suffix}"


def format_provider_error(
    category: str,
    data: dict[str, Any],
) -> str | None:

    if data.get("success"):
        return None

    error = data.get("error")

    if not error:
        return None

    return f"""
LIVE PROVIDER STATUS

Category:
{category}

Status:
Live information is currently unavailable.

Reason:
{error}

Instructions:
Do not invent current information.
Do not guess prices, scores, news,
bookings, exchange rates or other live values.

Explain briefly in the user's preferred language
that this live provider is currently unavailable.

If provider configuration is required,
say that the feature needs provider setup.
""".strip()


# =========================================================
# CRYPTO
# =========================================================

def format_crypto(
    data: dict[str, Any],
) -> str | None:

    if not data.get("success"):
        return None

    return f"""
VERIFIED LIVE CRYPTOCURRENCY DATA

Asset:
{data.get('coin')}

Current price in US dollars:
${data.get('usd')}

Current price in Indian rupees:
₹{value_or_unknown(data.get('inr'))}

24-hour price change:
{
    value_or_unknown(
        data.get(
            'change24hUsd',
            data.get('change24h')
        ),
        ' percent'
    )
}

24-hour INR change:
{
    value_or_unknown(
        data.get('change24hInr'),
        ' percent'
    )
}

Market capitalization:
{value_or_unknown(data.get('marketCapUsd'))}

24-hour trading volume:
{value_or_unknown(data.get('volume24hUsd'))}

Last updated:
{value_or_unknown(data.get('lastUpdatedAt'))}

Data provider:
{data.get('source', 'CoinGecko')}

Instructions:
Use these supplied live values exactly.
Explain the current price naturally.
Explain the 24-hour movement if available.
Do not invent missing market values.
Do not give a trading recommendation unless
the user specifically asks for analysis.
""".strip()


# =========================================================
# WEATHER
# =========================================================

def format_weather(
    data: dict[str, Any],
) -> str | None:

    if not data.get("success"):
        return None

    forecast = (
        data.get("forecast")
        or []
    )

    forecast_lines = []

    for index, day in enumerate(
        forecast
    ):

        if index == 0:
            label = "Today"

        elif index == 1:
            label = "Tomorrow"

        else:
            label = (
                f"Day {index + 1}"
            )

        forecast_lines.append(
            f"""
{label}

Date:
{day.get('date')}

Condition:
{day.get('condition')}

Maximum temperature:
{
    value_or_unknown(
        day.get(
            'maximumTemperature'
        ),
        ' degrees Celsius'
    )
}

Minimum temperature:
{
    value_or_unknown(
        day.get(
            'minimumTemperature'
        ),
        ' degrees Celsius'
    )
}

Rain probability:
{
    value_or_unknown(
        day.get(
            'rainProbability'
        ),
        ' percent'
    )
}

Sunrise:
{
    value_or_unknown(
        day.get('sunrise')
    )
}

Sunset:
{
    value_or_unknown(
        day.get('sunset')
    )
}
""".strip()
        )

    forecast_text = (
        "\n\n".join(
            forecast_lines
        )
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
{
    value_or_unknown(
        data.get(
            'observationTime'
        )
    )
}

Current condition:
{
    value_or_unknown(
        data.get('condition')
    )
}

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

Humidity:
{
    value_or_unknown(
        data.get('humidity'),
        ' percent'
    )
}

Rain:
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

FORECAST

{forecast_text}

Data provider:
{
    data.get(
        'source',
        'Open-Meteo'
    )
}

Instructions:
Use these live weather values exactly.
Answer in the user's preferred language.
Clearly separate current weather from forecast.
Do not invent weather alerts.
""".strip()


# =========================================================
# STOCKS
# =========================================================

def format_stock(
    data: dict[str, Any],
) -> str | None:

    if not data.get("success"):
        return None

    currency = data.get(
        "currency",
        "",
    )

    currency_symbol = (
        "₹"
        if currency == "INR"
        else "$"
    )

    change_percent = (
        data.get(
            "changePercent"
        )
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
This market quote may be delayed.

Instructions:
Use these supplied values exactly.
Explain whether the instrument moved up or down.
Do not invent intraday values.
Do not invent support, resistance,
targets or predictions.
""".strip()


# =========================================================
# GOLD
# =========================================================

def format_gold(
    data: dict[str, Any],
) -> str | None:

    if not data.get("success"):
        return None

    return f"""
VERIFIED GOLD DATA

Asset:
{data.get('name', 'Gold')}

Symbol:
{data.get('symbol', 'XAU')}

USD per troy ounce:
{
    value_or_unknown(
        data.get('usdPerOunce')
    )
}

USD per gram:
{
    value_or_unknown(
        data.get('usdPerGram')
    )
}

Updated at:
{
    value_or_unknown(
        data.get('updatedAt')
    )
}

Data provider:
{data.get('source')}

Instructions:
Use the supplied gold values exactly.

If this is international spot gold,
do not claim it is the Indian
22K or 24K jewellery retail price.

Do not invent local jewellery rates.
""".strip()


# =========================================================
# CURRENCY
# =========================================================

def format_currency(
    data: dict[str, Any],
) -> str | None:

    if not data.get("success"):
        return None

    return f"""
VERIFIED CURRENCY EXCHANGE DATA

Base currency:
{data.get('base')}

Quote currency:
{data.get('quote')}

Reference exchange rate:
{data.get('rate')}

Amount:
{data.get('amount')}

Converted amount:
{data.get('convertedAmount')}

Rate date:
{data.get('date')}

Data provider:
{data.get('source')}

Instructions:
Use these supplied exchange-rate
values exactly.

Explain that this is a reference
exchange rate.

Actual bank, card or cash exchange
rates may differ.
""".strip()


# =========================================================
# NEWS
# =========================================================

def format_news(
    data: dict[str, Any],
) -> str | None:

    if not data.get("success"):
        return None

    lines = []

    for index, item in enumerate(
        data.get("items") or [],
        start=1,
    ):

        lines.append(
            (
                f"{index}. "
                f"{item.get('title')} "
                f"| Source: "
                f"{item.get('source')} "
                f"| Published: "
                f"{item.get('published')}"
            )
        )

    news_text = "\n".join(
        lines
    )

    return f"""
VERIFIED RECENT NEWS SEARCH RESULTS

Search query:
{data.get('query')}

Results:

{news_text}

Data provider:
{data.get('source')}

Instructions:
Summarize only the returned headlines.
Do not invent article details.
Do not claim information that is not
present in these results.

If the user asks for more details,
explain only what can safely be inferred
from the supplied results.
""".strip()


# =========================================================
# SPORTS
# =========================================================

def format_sports(
    data: dict[str, Any],
) -> str | None:

    if not data.get(
        "success"
    ):
        return None


    sport = (
        data.get("sport")
        or "Unknown"
    )


    intent = (
        data.get("intent")
        or "GENERAL"
    )


    team_name = (
        data.get("team")
        or "Unknown"
    )


    country = (
        data.get("country")
        or "Unknown"
    )


    # =====================================================
    # LIVE
    # =====================================================

    live_event = (
        data.get(
            "liveEvent"
        )
        or {}
    )


    if (
        data.get(
            "liveScore"
        )
        and
        live_event
    ):

        live_text = f"""
Verified live match:

Match:
{live_event.get('event')}

Competition:
{value_or_unknown(live_event.get('league'))}

Round:
{value_or_unknown(live_event.get('round'))}

Home team:
{live_event.get('homeTeam')}

Away team:
{live_event.get('awayTeam')}

Current score:
{live_event.get('homeScore')} - {live_event.get('awayScore')}

Match status:
{value_or_unknown(live_event.get('statusLong'))}

Status code:
{value_or_unknown(live_event.get('status'))}

Elapsed time:
{
    value_or_unknown(
        live_event.get('elapsed'),
        ' minutes'
    )
}

Match time:
{value_or_unknown(live_event.get('date'))}

Venue:
{value_or_unknown(live_event.get('venue'))}

Venue city:
{value_or_unknown(live_event.get('venueCity'))}
""".strip()

    else:

        live_text = (
            "No verified live match "
            "was returned for this team."
        )


    # =====================================================
    # UPCOMING
    # =====================================================

    upcoming_lines = []


    for index, item in enumerate(
        data.get(
            "nextEvents"
        )
        or [],
        start=1,
    ):

        upcoming_lines.append(
            f"""
{index}. {item.get('event')}

Competition:
{value_or_unknown(item.get('league'))}

Round:
{value_or_unknown(item.get('round'))}

Date and time:
{value_or_unknown(item.get('date'))}

Venue:
{value_or_unknown(item.get('venue'))}

City:
{value_or_unknown(item.get('venueCity'))}

Status:
{value_or_unknown(item.get('statusLong'))}
""".strip()
        )


    upcoming_text = (
        "\n\n".join(
            upcoming_lines
        )
        if upcoming_lines
        else
        "No upcoming fixtures were returned."
    )


    # =====================================================
    # RECENT
    # =====================================================

    recent_lines = []


    for index, item in enumerate(
        data.get(
            "recentEvents"
        )
        or [],
        start=1,
    ):

        recent_lines.append(
            f"""
{index}. {item.get('event')}

Competition:
{value_or_unknown(item.get('league'))}

Date:
{value_or_unknown(item.get('date'))}

Final/latest score:
{item.get('homeScore')} - {item.get('awayScore')}

Status:
{value_or_unknown(item.get('statusLong'))}

Venue:
{value_or_unknown(item.get('venue'))}
""".strip()
        )


    recent_text = (
        "\n\n".join(
            recent_lines
        )
        if recent_lines
        else
        "No recent results were returned."
    )


    return f"""
VERIFIED SPORTS DATA

Sport:
{sport}

Detected request:
{intent}

Team:
{team_name}

Country:
{country}

National team:
{value_or_unknown(data.get('nationalTeam'))}

Founded:
{value_or_unknown(data.get('founded'))}

Home venue:
{value_or_unknown(data.get('venue'))}

Venue city:
{value_or_unknown(data.get('venueCity'))}

LIVE MATCH

{live_text}

UPCOMING FIXTURES

{upcoming_text}

RECENT RESULTS

{recent_text}

Data provider:
{data.get('source')}

Provider platform:
{data.get('providerType')}

Instructions:

Use only the supplied provider data
for live scores, fixtures and results.

If a verified live event exists,
give the score first.

If liveScore is false,
do not imply that a match is live.

If the user asked for schedule,
focus on upcoming fixtures.

If the user asked for recent result,
focus on recent results.

Never invent:
scores,
fixtures,
rankings,
league tables,
match status,
players,
or statistics.

Convert the answer naturally into
the user's preferred language.

Do not mention implementation details,
API keys or provider routing.
""".strip()

# =========================================================
# HOLIDAYS
# =========================================================

def format_holidays(
    data: dict[str, Any],
) -> str | None:

    if not data.get("success"):
        return None

    holiday_lines = []

    for item in (
        data.get("holidays")
        or []
    )[:25]:

        holiday_lines.append(
            (
                f"{item.get('date')} "
                f"- {item.get('name')}"
            )
        )

    holiday_text = "\n".join(
        holiday_lines
    )

    return f"""
VERIFIED PUBLIC HOLIDAY DATA

Country code:
{data.get('countryCode')}

Year:
{data.get('year')}

Public holidays:

{holiday_text}

Data provider:
{data.get('source')}

Instructions:
Use these supplied holiday dates exactly.

Do not automatically claim
all private businesses,
schools or local offices are closed,
because local rules may differ.
""".strip()


# =========================================================
# MOVIES
# =========================================================

def format_movies(
    data: dict[str, Any],
) -> str | None:

    if not data.get("success"):
        return None

    movie_lines = []

    for index, item in enumerate(
        data.get("movies") or [],
        start=1,
    ):

        movie_lines.append(
            f"""
{index}. {item.get('title')}

Original title:
{item.get('originalTitle')}

Release date:
{item.get('releaseDate')}

Rating:
{item.get('rating')}

Vote count:
{item.get('voteCount')}

Original language:
{item.get('language')}

Overview:
{item.get('overview')}
""".strip()
        )

    movies_text = (
        "\n\n".join(
            movie_lines
        )
    )

    return f"""
VERIFIED MOVIE DATABASE RESULTS

Search query:
{data.get('query')}

{movies_text}

Data provider:
{data.get('source')}

Instructions:
Use only supplied movie metadata
for current database facts.

Do not invent box-office values,
streaming availability or release dates.
""".strip()


# =========================================================
# WIKIPEDIA
# =========================================================

def format_wikipedia(
    data: dict[str, Any],
) -> str | None:

    if not data.get("success"):
        return None

    result_lines = []

    for item in (
        data.get("results")
        or []
    ):

        result_lines.append(
            (
                f"{item.get('title')}: "
                f"{item.get('snippet')}"
            )
        )

    result_text = "\n\n".join(
        result_lines
    )

    return f"""
WIKIPEDIA SEARCH RESULTS

Search query:
{data.get('query')}

{result_text}

Source:
Wikipedia

Instructions:
Use the retrieved Wikipedia search
context as supporting information.

Do not invent citations.
Do not claim the search snippets contain
information that is not actually present.
""".strip()


# =========================================================
# YOUTUBE
# =========================================================

def format_youtube(
    data: dict[str, Any],
) -> str | None:

    if not data.get("success"):
        return None

    video_lines = []

    for index, item in enumerate(
        data.get("videos") or [],
        start=1,
    ):

        video_lines.append(
            f"""
{index}. {item.get('title')}

Channel:
{item.get('channelTitle')}

Published:
{item.get('publishedAt')}

Description:
{item.get('description')}

URL:
{item.get('url')}
""".strip()
        )

    videos_text = (
        "\n\n".join(
            video_lines
        )
    )

    return f"""
YOUTUBE SEARCH RESULTS

Search query:
{data.get('query')}

{videos_text}

Data provider:
YouTube Data API

Instructions:
Recommend or summarize the returned
search metadata naturally.

Do not claim that you watched a video
unless its actual content was retrieved.
""".strip()


# =========================================================
# CALCULATOR
# =========================================================

def format_calculator(
    data: dict[str, Any],
) -> str | None:

    if not data.get("success"):
        return None

    return f"""
VERIFIED CALCULATION RESULT

Expression:
{data.get('expression')}

Result:
{data.get('result')}

Calculation engine:
{data.get('source')}

Instructions:
Return the calculation result directly.
Explain the calculation briefly
if the user asks for steps.
""".strip()


# =========================================================
# UNIT CONVERTER
# =========================================================

def format_unit(
    data: dict[str, Any],
) -> str | None:

    if not data.get("success"):
        return None

    return f"""
VERIFIED UNIT CONVERSION

Input:
{data.get('value')} {data.get('fromUnit')}

Converted value:
{data.get('result')} {data.get('toUnit')}

Conversion engine:
{data.get('source')}

Instructions:
Return the converted value directly.
Do not alter the supplied conversion.
""".strip()


# =========================================================
# TRAVEL
# =========================================================

def format_travel(
    data: dict[str, Any],
) -> str | None:

    if not data.get("success"):
        return None

    return f"""
TRAVEL BOOKING HANDOFF

Travel mode:
{data.get('mode')}

Origin:
{
    value_or_unknown(
        data.get('origin')
    )
}

Destination:
{
    value_or_unknown(
        data.get('destination')
    )
}

Transactional booking completed:
{data.get('transactionalBooking')}

Booking information:
{data.get('message')}

Booking destination:
{data.get('bookingLink')}

Instructions:
Do not claim that a ticket has been booked.

Do not claim that payment has been made.

Explain that final booking,
passenger details,
availability,
fare,
payment and confirmation
must happen through the booking provider.
""".strip()


# =========================================================
# MAIN FORMAT ROUTER
# =========================================================

def format_live_result(
    result: dict[str, Any],
) -> str | None:

    if not result.get("live"):
        return None

    category = result.get(
        "category"
    )

    data = result.get(
        "data"
    )

    if not isinstance(
        data,
        dict,
    ):
        return None

    if not data.get(
        "success"
    ):
        return format_provider_error(
            str(category),
            data,
        )

    formatters = {
        "CRYPTO": format_crypto,
        "WEATHER": format_weather,
        "STOCK": format_stock,
        "GOLD": format_gold,
        "CURRENCY": format_currency,
        "NEWS": format_news,
        "SPORTS": format_sports,
        "HOLIDAY": format_holidays,
        "MOVIE": format_movies,
        "WIKIPEDIA": format_wikipedia,
        "YOUTUBE": format_youtube,
        "CALCULATOR": format_calculator,
        "UNIT": format_unit,
        "TRAIN": format_travel,
        "BUS": format_travel,
        "FLIGHT": format_travel,
    }

    formatter = formatters.get(
        category
    )

    if formatter:
        return formatter(
            data
        )

    if category == "FUEL":
        return format_provider_error(
            category,
            data,
        )

    return None