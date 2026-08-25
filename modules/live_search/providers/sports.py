from __future__ import annotations

import os
import re
import time
from datetime import date, timedelta
from typing import Any

import requests
from dotenv import load_dotenv


load_dotenv()


API_FOOTBALL_BASE_URL = (
    "https://v3.football.api-sports.io"
)

THESPORTSDB_BASE_URL = (
    "https://www.thesportsdb.com/api/v1/json"
)

API_BASKETBALL_BASE_URL = (
    "https://v1.basketball.api-sports.io"
)

API_VOLLEYBALL_BASE_URL = (
    "https://v1.volleyball.api-sports.io"
)

API_HOCKEY_BASE_URL = (
    "https://v1.hockey.api-sports.io"
)

API_FORMULA1_BASE_URL = (
    "https://v1.formula-1.api-sports.io"
)

REQUEST_TIMEOUT = 12

TEAM_CACHE_TTL_SECONDS = (
    6 * 60 * 60
)

_team_cache: dict[
    str,
    dict[str, Any],
] = {}

SEASON_CACHE_TTL_SECONDS = (
    12 * 60 * 60
)

_season_cache: dict[
    int,
    dict[str, Any],
] = {}


# =========================================================
# SPORTS
# =========================================================

SPORT_ALIASES = {
    "CRICKET": (
        "cricket",
        "ipl",
        "t20",
        "t20i",
        "odi",
        "test match",
        "world test championship",
        "champions trophy",

        "క్రికెట్",
        "ఐపీఎల్",
        "టి20",
        "వన్డే",
        "టెస్ట్ మ్యాచ్",
    ),

    "FOOTBALL": (
        "football",
        "soccer",
        "fifa",
        "premier league",
        "champions league",
        "isl",

        "ఫుట్‌బాల్",
        "సాకర్",
    ),

    "HOCKEY": (
        "hockey",
        "field hockey",
        "hockey india",
        "హాకీ",
    ),

    "BADMINTON": (
        "badminton",
        "bwf",
        "బ్యాడ్మింటన్",
    ),

    "KABADDI": (
        "kabaddi",
        "pro kabaddi",
        "pkl",
        "కబడ్డీ",
    ),

    "TENNIS": (
        "tennis",
        "atp",
        "wta",
        "grand slam",
        "టెన్నిస్",
    ),

    "CHESS": (
        "chess",
        "fide",
        "grandmaster",
        "చెస్",
    ),

    "ATHLETICS": (
        "athletics",
        "javelin",
        "running",
        "track and field",
        "athlete",

        "అథ్లెటిక్స్",
        "జావెలిన్",
    ),

    "WRESTLING": (
        "wrestling",
        "wrestler",
        "కుస్తీ",
        "రెజ్లింగ్",
    ),

    "BOXING": (
        "boxing",
        "boxer",
        "బాక్సింగ్",
    ),

    "SHOOTING": (
        "shooting",
        "rifle",
        "pistol shooting",
        "షూటింగ్",
    ),

    "TABLE_TENNIS": (
        "table tennis",
        "ping pong",
        "టేబుల్ టెన్నిస్",
    ),

    "VOLLEYBALL": (
        "volleyball",
        "వాలీబాల్",
    ),

    "BASKETBALL": (
        "basketball",
        "nba",
        "బాస్కెట్‌బాల్",
    ),

    "FORMULA_1": (
        "formula 1",
        "formula one",
        "f1",
        "ఫార్ములా 1",
    ),
}


SPORT_ENTITY_MAP = {
    # Cricket
    "virat kohli":
        "CRICKET",

    "rohit sharma":
        "CRICKET",

    "jasprit bumrah":
        "CRICKET",

    "shubman gill":
        "CRICKET",

    "hardik pandya":
        "CRICKET",

    "ms dhoni":
        "CRICKET",

    "sachin tendulkar":
        "CRICKET",

    # Football
    "sunil chhetri":
        "FOOTBALL",

    "gurpreet singh sandhu":
        "FOOTBALL",

    # Badminton
    "pv sindhu":
        "BADMINTON",

    "p v sindhu":
        "BADMINTON",

    "lakshya sen":
        "BADMINTON",

    "kidambi srikanth":
        "BADMINTON",

    "saina nehwal":
        "BADMINTON",

    # Athletics
    "neeraj chopra":
        "ATHLETICS",

    # Chess
    "gukesh":
        "CHESS",

    "d gukesh":
        "CHESS",

    "praggnanandhaa":
        "CHESS",

    "r praggnanandhaa":
        "CHESS",

    "viswanathan anand":
        "CHESS",

    # Boxing
    "nikhat zareen":
        "BOXING",

    "lovlina borgohain":
        "BOXING",

    # Wrestling
    "aman sehrawat":
        "WRESTLING",

    # Shooting
    "manu bhaker":
        "SHOOTING",
}


# =========================================================
# INTENTS
# =========================================================

LIVE_TERMS = (
    "live score",
    "live match",
    "current score",
    "score now",
    "live",

    "లైవ్ స్కోర్",
    "లైవ్ మ్యాచ్",
    "ప్రస్తుత స్కోర్",
)


SCHEDULE_TERMS = (
    "schedule",
    "fixture",
    "fixtures",
    "next match",
    "upcoming match",
    "today match",
    "match today",
    "next game",

    "షెడ్యూల్",
    "తర్వాతి మ్యాచ్",
    "ఈరోజు మ్యాచ్",
)


RESULT_TERMS = (
    "result",
    "results",
    "last match",
    "previous match",
    "who won",
    "won",
    "lost",
    "latest result",

    "ఫలితం",
    "ఎవరు గెలిచారు",
    "గెలిచింది",
)


RANKING_TERMS = (
    "ranking",
    "rankings",
    "rank",
    "world ranking",
    "standings",
    "points table",

    "ర్యాంకింగ్",
    "పాయింట్స్ టేబుల్",
)


DETAIL_TERMS = (
    "details",
    "player details",
    "team details",
    "profile",
    "information",
    "about",

    "వివరాలు",
    "గురించి",
)


REMOVE_INTENT_PHRASES = {
    "live score",
    "live match",
    "current score",
    "score now",
    "match score",

    "schedule",
    "fixtures",
    "fixture",
    "next match",
    "upcoming match",
    "today match",
    "match today",

    "latest result",
    "last match",
    "previous match",
    "result",
    "results",

    "ranking",
    "rankings",
    "world ranking",
    "rank",
    "standings",
    "points table",

    "player details",
    "team details",
    "details",
    "profile",

    "లైవ్ స్కోర్",
    "లైవ్ మ్యాచ్",
    "ప్రస్తుత స్కోర్",

    "షెడ్యూల్",
    "తర్వాతి మ్యాచ్",
    "ఈరోజు మ్యాచ్",

    "ఫలితం",
    "ర్యాంకింగ్",
    "పాయింట్స్ టేబుల్",

    "వివరాలు",
    "గురించి",
}


# =========================================================
# TEXT HELPERS
# =========================================================

def clean_text(
    value: Any,
) -> str:

    return re.sub(
        r"\s+",
        " ",
        str(value or "")
        .strip(),
    )


def normalize_text(
    value: Any,
) -> str:

    return clean_text(
        value
    ).casefold()


def contains_any(
    text: str,
    terms: tuple[str, ...],
) -> bool:

    normalized = (
        normalize_text(
            text
        )
    )

    return any(
        normalize_text(term)
        in normalized

        for term in terms
    )


# =========================================================
# SPORT DETECTION
# =========================================================

def detect_sport(
    question: str,
) -> str | None:

    normalized = (
        normalize_text(
            question
        )
    )


    for (
        entity,
        sport,
    ) in sorted(
        SPORT_ENTITY_MAP.items(),
        key=lambda item:
            len(item[0]),
        reverse=True,
    ):

        if (
            entity.casefold()
            in normalized
        ):
            return sport


    for (
        sport,
        aliases,
    ) in SPORT_ALIASES.items():

        for alias in sorted(
            aliases,
            key=len,
            reverse=True,
        ):

            if (
                normalize_text(alias)
                in normalized
            ):
                return sport


    return None


def detect_sports_intent(
    question: str,
) -> str:

    if contains_any(
        question,
        LIVE_TERMS,
    ):
        return "LIVE_SCORE"


    if contains_any(
        question,
        SCHEDULE_TERMS,
    ):
        return "SCHEDULE"


    if contains_any(
        question,
        RESULT_TERMS,
    ):
        return "RESULT"


    if contains_any(
        question,
        RANKING_TERMS,
    ):
        return "RANKING"


    if contains_any(
        question,
        DETAIL_TERMS,
    ):
        return "DETAILS"


    return "GENERAL"


# =========================================================
# QUERY CLEANING
# =========================================================

def clean_sports_query(
    question: str,
    sport: str | None,
) -> str:

    text = clean_text(
        question
    )


    for phrase in sorted(
        REMOVE_INTENT_PHRASES,
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


    if sport:

        for alias in (
            SPORT_ALIASES.get(
                sport,
                (),
            )
        ):

            text = re.sub(
                re.escape(
                    alias
                ),
                " ",
                text,
                flags=re.IGNORECASE,
            )


    text = re.sub(
        (
            r"\b(?:"
            r"today|now|current|latest|"
            r"please|tell|me"
            r")\b"
        ),
        " ",
        text,
        flags=re.IGNORECASE,
    )


    text = (
        text
        .replace(
            "ఈరోజు",
            " ",
        )
        .replace(
            "ఇప్పుడు",
            " ",
        )
        .replace(
            "ప్రస్తుతం",
            " ",
        )
        .replace(
            "చెప్పు",
            " ",
        )
        .replace(
            "చెప్పండి",
            " ",
        )
    )


    return clean_text(
        text
    )


# =========================================================
# API SPORTS
# =========================================================

def get_api_sports_key() -> str:

    return clean_text(
        os.getenv(
            "API_SPORTS_KEY"
        )
    )


def api_football_request(
    endpoint: str,
    params: dict[
        str,
        Any,
    ] | None = None,
) -> dict[str, Any]:

    api_key = (
        get_api_sports_key()
    )


    if not api_key:

        raise RuntimeError(
            "API_SPORTS_KEY is not configured."
        )


    response = requests.get(
        (
            f"{API_FOOTBALL_BASE_URL}/"
            f"{endpoint.lstrip('/')}"
        ),

        headers={
            "x-apisports-key":
                api_key,

            "Accept":
                "application/json",
        },

        params=(
            params
            or {}
        ),

        timeout=
            REQUEST_TIMEOUT,
    )


    response.raise_for_status()


    payload = (
        response.json()
    )


    errors = (
        payload.get(
            "errors"
        )
    )


    if errors:

        raise RuntimeError(
            (
                "API-Football error: "
                f"{errors}"
            )
        )


    return payload

def api_sports_request(
    base_url: str,
    endpoint: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:

    api_key = (
        get_api_sports_key()
    )

    if not api_key:

        raise RuntimeError(
            "API_SPORTS_KEY is not configured."
        )

    response = requests.get(
        (
            f"{base_url}/"
            f"{endpoint.lstrip('/')}"
        ),

        headers={
            "x-apisports-key":
                api_key,

            "Accept":
                "application/json",
        },

        params=(
            params
            or {}
        ),

        timeout=
            REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    payload = response.json()

    errors = (
        payload.get("errors")
    )

    if errors:

        raise RuntimeError(
            (
                "API-Sports error: "
                f"{errors}"
            )
        )

    return payload

def is_current_season_plan_restricted(
    error: Exception | str,
) -> bool:

    text = str(
        error or ""
    ).casefold()

    return (
        "free plans do not have access "
        "to this season"
        in text
        or
        (
            "plan"
            in text
            and
            "season"
            in text
            and
            "2022 to 2024"
            in text
        )
    )


# =========================================================
# TEAM CACHE
# =========================================================

def get_cached_team(
    query: str,
) -> dict[str, Any] | None:

    key = normalize_text(
        query
    )


    cached = (
        _team_cache.get(
            key
        )
    )


    if not cached:
        return None


    age = (
        time.time()
        -
        float(
            cached.get(
                "storedAt",
                0,
            )
        )
    )


    if (
        age
        >
        TEAM_CACHE_TTL_SECONDS
    ):

        _team_cache.pop(
            key,
            None,
        )

        return None


    team = cached.get(
        "team"
    )


    if isinstance(
        team,
        dict,
    ):
        return team


    return None


def set_cached_team(
    query: str,
    team: dict[str, Any],
):

    _team_cache[
        normalize_text(
            query
        )
    ] = {
        "storedAt":
            time.time(),

        "team":
            team,
    }
    
def get_cached_season(
    team_id: int,
) -> int | None:

    cached = (
        _season_cache.get(
            int(team_id)
        )
    )

    if not cached:
        return None

    age = (
        time.time()
        -
        float(
            cached.get(
                "storedAt",
                0,
            )
        )
    )

    if (
        age
        >
        SEASON_CACHE_TTL_SECONDS
    ):

        _season_cache.pop(
            int(team_id),
            None,
        )

        return None

    season = cached.get(
        "season"
    )

    try:
        return int(
            season
        )

    except (
        TypeError,
        ValueError,
    ):
        return None


def set_cached_season(
    team_id: int,
    season: int,
):

    _season_cache[
        int(team_id)
    ] = {
        "storedAt":
            time.time(),

        "season":
            int(season),
    }


def get_api_football_season(
    team_id: int,
) -> int:

    cached = get_cached_season(
        team_id
    )

    if cached is not None:
        return cached

    payload = (
        api_football_request(
            "teams/seasons",
            {
                "team":
                    int(team_id),
            },
        )
    )

    raw_seasons = (
        payload.get(
            "response"
        )
        or []
    )

    seasons = []

    for value in raw_seasons:

        try:
            season = int(
                value
            )

        except (
            TypeError,
            ValueError,
        ):
            continue

        if (
            1900
            <= season
            <= 2100
        ):
            seasons.append(
                season
            )

    if not seasons:

        raise RuntimeError(
            "No accessible season was "
            "returned for this football team."
        )

    current_year = (
        date.today().year
    )

    # Prefer current year if the API
    # exposes it on the current Free plan.
    if current_year in seasons:

        selected_season = (
            current_year
        )

    else:

        # Otherwise use the most recent
        # accessible season.
        selected_season = max(
            seasons
        )

    set_cached_season(
        team_id,
        selected_season,
    )

    return selected_season    


# =========================================================
# FOOTBALL TEAM SELECTION
# =========================================================

def football_team_score(
    item: dict[str, Any],
    query: str,
) -> int:

    team = (
        item.get(
            "team"
        )
        or {}
    )


    name = normalize_text(
        team.get(
            "name"
        )
    )


    country = normalize_text(
        team.get(
            "country"
        )
    )


    code = normalize_text(
        team.get(
            "code"
        )
    )


    wanted = normalize_text(
        query
    )


    score = 0


    if name == wanted:
        score += 100

    elif (
        wanted
        and
        name.startswith(
            wanted
        )
    ):
        score += 50

    elif (
        wanted
        and
        wanted in name
    ):
        score += 25


    if (
        code
        and
        code == wanted
    ):
        score += 80


    if wanted in {
        "india",
        "ind",
    }:

        if country == "india":
            score += 40


        if (
            team.get(
                "national"
            )
            is True
        ):
            score += 50


        if name == "india":
            score += 100


    return score


def search_api_football_team(
    query: str,
) -> dict[str, Any] | None:

    cached = get_cached_team(
        query
    )


    if cached:
        return cached


    payload = (
        api_football_request(
            "teams",
            {
                "search":
                    query,
            },
        )
    )


    candidates = (
        payload.get(
            "response"
        )
        or []
    )


    if (
        not isinstance(
            candidates,
            list,
        )
        or
        not candidates
    ):
        return None


    best = max(
        candidates,
        key=lambda item:
            football_team_score(
                item,
                query,
            ),
    )


    team = (
        best.get(
            "team"
        )
        or {}
    )


    if not team.get(
        "id"
    ):
        return None


    normalized = {
        "id":
            team.get(
                "id"
            ),

        "name":
            team.get(
                "name"
            ),

        "code":
            team.get(
                "code"
            ),

        "country":
            team.get(
                "country"
            ),

        "founded":
            team.get(
                "founded"
            ),

        "national":
            team.get(
                "national"
            ),

        "logo":
            team.get(
                "logo"
            ),

        "venue":
            (
                best.get(
                    "venue"
                )
                or {}
            ),
    }


    set_cached_team(
        query,
        normalized,
    )


    return normalized


# =========================================================
# FOOTBALL FIXTURE NORMALIZER
# =========================================================

def normalize_api_football_fixture(
    item: dict[str, Any],
) -> dict[str, Any]:

    fixture = (
        item.get(
            "fixture"
        )
        or {}
    )


    status = (
        fixture.get(
            "status"
        )
        or {}
    )


    venue = (
        fixture.get(
            "venue"
        )
        or {}
    )


    league = (
        item.get(
            "league"
        )
        or {}
    )


    teams = (
        item.get(
            "teams"
        )
        or {}
    )


    home = (
        teams.get(
            "home"
        )
        or {}
    )


    away = (
        teams.get(
            "away"
        )
        or {}
    )


    goals = (
        item.get(
            "goals"
        )
        or {}
    )


    return {
        "eventId":
            fixture.get(
                "id"
            ),

        "event":
            (
                f"{home.get('name') or 'Unknown'} "
                f"vs "
                f"{away.get('name') or 'Unknown'}"
            ),

        "date":
            fixture.get(
                "date"
            ),

        "timestamp":
            fixture.get(
                "timestamp"
            ),

        "time":
            fixture.get(
                "date"
            ),

        "timezone":
            fixture.get(
                "timezone"
            ),

        "league":
            league.get(
                "name"
            ),

        "leagueCountry":
            league.get(
                "country"
            ),

        "round":
            league.get(
                "round"
            ),

        "sport":
            "Football",

        "venue":
            venue.get(
                "name"
            ),

        "venueCity":
            venue.get(
                "city"
            ),

        "status":
            status.get(
                "short"
            ),

        "statusLong":
            status.get(
                "long"
            ),

        "elapsed":
            status.get(
                "elapsed"
            ),

        "homeTeamId":
            home.get(
                "id"
            ),

        "homeTeam":
            home.get(
                "name"
            ),

        "awayTeamId":
            away.get(
                "id"
            ),

        "awayTeam":
            away.get(
                "name"
            ),

        "homeScore":
            goals.get(
                "home"
            ),

        "awayScore":
            goals.get(
                "away"
            ),

        "homeWinner":
            home.get(
                "winner"
            ),

        "awayWinner":
            away.get(
                "winner"
            ),
    }


# =========================================================
# FOOTBALL FIXTURES
# =========================================================

def get_api_football_fixtures(
    team_id: int,
    *,
    mode: str,
    limit: int = 5,
) -> list[dict[str, Any]]:

    today = date.today()

    normalized_mode = (
        str(mode or "")
        .strip()
        .upper()
    )

    season = (
        get_api_football_season(
            team_id
        )
    )

    if normalized_mode == "UPCOMING":

        from_date = today

        to_date = (
            today
            + timedelta(
                days=365
            )
        )

    elif normalized_mode == "RECENT":

        from_date = (
            today
            - timedelta(
                days=365
            )
        )

        to_date = today

    else:

        raise ValueError(
            "Fixture mode must be "
            "UPCOMING or RECENT."
        )

    params: dict[
        str,
        Any,
    ] = {
        "team":
            int(team_id),

        "season":
            int(season),

        "from":
            from_date.isoformat(),

        "to":
            to_date.isoformat(),

        "timezone":
            "Asia/Kolkata",
    }

    payload = (
        api_football_request(
            "fixtures",
            params,
        )
    )

    fixtures = []

    for item in (
        payload.get(
            "response"
        )
        or []
    ):

        if not isinstance(
            item,
            dict,
        ):
            continue

        fixtures.append(
            normalize_api_football_fixture(
                item
            )
        )

    # =========================================
    # UPCOMING
    # =========================================

    if (
        normalized_mode
        == "UPCOMING"
    ):

        upcoming_statuses = {
            "TBD",
            "NS",
            "PST",
        }

        fixtures = [
            item

            for item in fixtures

            if (
                item.get(
                    "status"
                )
                in upcoming_statuses
            )
        ]

        fixtures.sort(
            key=lambda item: (
                item.get(
                    "timestamp"
                )
                or 0
            )
        )

    # =========================================
    # RECENT RESULTS
    # =========================================

    else:

        completed_statuses = {
            "FT",
            "AET",
            "PEN",
        }

        fixtures = [
            item

            for item in fixtures

            if (
                item.get(
                    "status"
                )
                in completed_statuses
            )
        ]

        fixtures.sort(
            key=lambda item: (
                item.get(
                    "timestamp"
                )
                or 0
            ),
            reverse=True,
        )

    return fixtures[
        :max(
            1,
            int(limit),
        )
    ]

def get_api_football_live_event(
    team_id: int,
) -> dict[str, Any] | None:

    payload = (
        api_football_request(
            "fixtures",
            {
                "live":
                    "all",

                "timezone":
                    "Asia/Kolkata",
            },
        )
    )

    responses = (
        payload.get(
            "response"
        )
        or []
    )

    if not isinstance(
        responses,
        list,
    ):
        return None

    for item in responses:

        if not isinstance(
            item,
            dict,
        ):
            continue

        teams = (
            item.get(
                "teams"
            )
            or {}
        )

        home = (
            teams.get(
                "home"
            )
            or {}
        )

        away = (
            teams.get(
                "away"
            )
            or {}
        )

        home_id = (
            home.get(
                "id"
            )
        )

        away_id = (
            away.get(
                "id"
            )
        )

        if team_id not in {
            home_id,
            away_id,
        }:
            continue

        normalized = (
            normalize_api_football_fixture(
                item
            )
        )

        status = (
            normalized.get(
                "status"
            )
        )

        # Only actual in-progress states
        # are treated as LIVE.
        live_statuses = {
            "1H",
            "HT",
            "2H",
            "ET",
            "BT",
            "P",
            "INT",
            "LIVE",
        }

        if (
            status
            in live_statuses
        ):
            return normalized

    return None

def get_thesportsdb_key() -> str:

    return clean_text(
        os.getenv(
            "THESPORTSDB_API_KEY"
        )
        or "123"
    )


def normalize_thesportsdb_event(
    item: dict[str, Any],
) -> dict[str, Any]:

    return {
        "eventId":
            item.get(
                "idEvent"
            ),

        "event":
            item.get(
                "strEvent"
            ),

        "date":
            item.get(
                "strTimestamp"
            )
            or item.get(
                "dateEvent"
            ),

        "timestamp":
            None,

        "time":
            item.get(
                "strTime"
            ),

        "timezone":
            None,

        "league":
            item.get(
                "strLeague"
            ),

        "leagueCountry":
            item.get(
                "strCountry"
            ),

        "round":
            item.get(
                "intRound"
            ),

        "sport":
            item.get(
                "strSport"
            )
            or "Soccer",

        "venue":
            item.get(
                "strVenue"
            ),

        "venueCity":
            None,

        "status":
            item.get(
                "strStatus"
            ),

        "statusLong":
            item.get(
                "strStatus"
            ),

        "elapsed":
            None,

        "homeTeamId":
            item.get(
                "idHomeTeam"
            ),

        "homeTeam":
            item.get(
                "strHomeTeam"
            ),

        "awayTeamId":
            item.get(
                "idAwayTeam"
            ),

        "awayTeam":
            item.get(
                "strAwayTeam"
            ),

        "homeScore":
            item.get(
                "intHomeScore"
            ),

        "awayScore":
            item.get(
                "intAwayScore"
            ),

        "homeWinner":
            None,

        "awayWinner":
            None,
    }


def search_thesportsdb_football_team(
    query: str,
) -> dict[str, Any] | None:

    api_key = (
        get_thesportsdb_key()
    )

    response = requests.get(
        (
            f"{THESPORTSDB_BASE_URL}/"
            f"{api_key}/"
            "searchteams.php"
        ),

        params={
            "t":
                query,
        },

        timeout=
            REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    payload = (
        response.json()
    )

    teams = (
        payload.get(
            "teams"
        )
        or []
    )

    if not isinstance(
        teams,
        list,
    ):
        return None

    wanted = normalize_text(
        query
    )

    candidates = []

    for team in teams:

        if not isinstance(
            team,
            dict,
        ):
            continue

        sport = normalize_text(
            team.get(
                "strSport"
            )
        )

        if sport != "soccer":
            continue

        name = normalize_text(
            team.get(
                "strTeam"
            )
        )

        country = normalize_text(
            team.get(
                "strCountry"
            )
        )

        score = 0

        if name == wanted:
            score += 100

        elif wanted in name:
            score += 30

        if (
            wanted == "india"
            and
            country == "india"
        ):
            score += 50

        candidates.append(
            (
                score,
                team,
            )
        )

    if not candidates:
        return None

    candidates.sort(
        key=lambda value:
            value[0],
        reverse=True,
    )

    return candidates[0][1]


def get_thesportsdb_schedule(
    query: str,
    limit: int = 5,
) -> list[dict[str, Any]]:

    team = (
        search_thesportsdb_football_team(
            query
        )
    )

    if not team:
        return []

    team_id = clean_text(
        team.get(
            "idTeam"
        )
    )

    if not team_id:
        return []

    api_key = (
        get_thesportsdb_key()
    )

    response = requests.get(
        (
            f"{THESPORTSDB_BASE_URL}/"
            f"{api_key}/"
            "eventsnext.php"
        ),

        params={
            "id":
                team_id,
        },

        timeout=
            REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    payload = (
        response.json()
    )

    events = []

    for item in (
        payload.get(
            "events"
        )
        or []
    ):

        if not isinstance(
            item,
            dict,
        ):
            continue

        events.append(
            normalize_thesportsdb_event(
                item
            )
        )

    return events[
        :max(
            1,
            int(limit),
        )
    ]


def get_thesportsdb_recent_results(
    query: str,
    limit: int = 5,
) -> list[dict[str, Any]]:

    team = (
        search_thesportsdb_football_team(
            query
        )
    )

    if not team:
        return []

    team_id = clean_text(
        team.get(
            "idTeam"
        )
    )

    if not team_id:
        return []

    api_key = (
        get_thesportsdb_key()
    )

    response = requests.get(
        (
            f"{THESPORTSDB_BASE_URL}/"
            f"{api_key}/"
            "eventslast.php"
        ),

        params={
            "id":
                team_id,
        },

        timeout=
            REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    payload = (
        response.json()
    )

    events = []

    for item in (
        payload.get(
            "results"
        )
        or []
    ):

        if not isinstance(
            item,
            dict,
        ):
            continue

        events.append(
            normalize_thesportsdb_event(
                item
            )
        )

    return events[
        :max(
            1,
            int(limit),
        )
    ]

# =========================================================
# FOOTBALL PROVIDER
# =========================================================

def get_football_data(
    question: str,
    intent: str,
    query: str,
) -> dict[str, Any]:

    if not query:

        return {
            "success":
                False,

            "sport":
                "FOOTBALL",

            "intent":
                intent,

            "error":
                (
                    "Please include a football "
                    "team or country name."
                ),

            "source":
                "API-Football",
        }


    if not get_api_sports_key():

        return {
            "success":
                False,

            "sport":
                "FOOTBALL",

            "intent":
                intent,

            "query":
                query,

            "configurationRequired":
                True,

            "error":
                (
                    "API_SPORTS_KEY "
                    "is not configured."
                ),

            "source":
                "API-Football",
        }


    try:

        team = (
            search_api_football_team(
                query
            )
        )


        if not team:

            return {
                "success":
                    False,

                "sport":
                    "FOOTBALL",

                "intent":
                    intent,

                "query":
                    query,

                "error":
                    (
                        "Football team not found: "
                        f"{query}"
                    ),

                "source":
                    "API-Football",
            }


        team_id = int(
            team[
                "id"
            ]
        )


        live_event = None

        next_events: list[
            dict[str, Any]
        ] = []

        recent_events: list[
            dict[str, Any]
        ] = []


        provider_source = (
            "API-Football"
        )


        provider_type = (
            "API-Sports"
        )


        # =====================================
        # LIVE SCORE
        # =====================================

        if intent == "LIVE_SCORE":

            live_event = (
                get_api_football_live_event(
                    team_id
                )
            )

            # IMPORTANT:
            # If no match is live,
            # do NOT call API-Football
            # current-season fixtures because
            # Free plan blocks the season.
            #
            # Use TheSportsDB only to provide
            # next fixture context.
            if live_event is None:

                try:

                    next_events = (
                        get_thesportsdb_schedule(
                            query,
                            limit=3,
                        )
                    )

                    if next_events:

                        provider_source = (
                            "API-Football + "
                            "TheSportsDB"
                        )

                        provider_type = (
                            "Hybrid sports provider"
                        )

                except Exception as error:

                    print(
                        "SPORTS FALLBACK "
                        "SCHEDULE ERROR:",
                        str(error),
                    )


        # =====================================
        # SCHEDULE
        # =====================================

        elif intent == "SCHEDULE":

            try:

                next_events = (
                    get_thesportsdb_schedule(
                        query,
                        limit=5,
                    )
                )

            except Exception as error:

                print(
                    "SPORTS SCHEDULE "
                    "FALLBACK ERROR:",
                    str(error),
                )

                next_events = []


            provider_source = (
                "TheSportsDB"
            )

            provider_type = (
                "Sports schedule database"
            )


        # =====================================
        # RECENT RESULTS
        # =====================================

        elif intent == "RESULT":

            try:

                recent_events = (
                    get_thesportsdb_recent_results(
                        query,
                        limit=5,
                    )
                )

            except Exception as error:

                print(
                    "SPORTS RESULT "
                    "FALLBACK ERROR:",
                    str(error),
                )

                recent_events = []


            provider_source = (
                "TheSportsDB"
            )

            provider_type = (
                "Sports results database"
            )


        # =====================================
        # RANKING
        # =====================================

        elif intent == "RANKING":

            return {
                "success":
                    False,

                "sport":
                    "FOOTBALL",

                "intent":
                    intent,

                "query":
                    query,

                "team":
                    team.get(
                        "name"
                    ),

                "country":
                    team.get(
                        "country"
                    ),

                "error":
                    (
                        "Please specify the "
                        "league or competition "
                        "for football standings."
                    ),

                "source":
                    "API-Football",
            }


        return {
            "success":
                True,

            "sport":
                "FOOTBALL",

            "intent":
                intent,

            "query":
                query,

            "team":
                team.get(
                    "name"
                ),

            "teamId":
                team.get(
                    "id"
                ),

            "teamCode":
                team.get(
                    "code"
                ),

            "nationalTeam":
                team.get(
                    "national"
                ),

            "country":
                team.get(
                    "country"
                ),

            "founded":
                team.get(
                    "founded"
                ),

            "venue":
                (
                    team.get(
                        "venue"
                    )
                    or {}
                )
                .get(
                    "name"
                ),

            "venueCity":
                (
                    team.get(
                        "venue"
                    )
                    or {}
                )
                .get(
                    "city"
                ),

            "league":
                None,

            "nextEvents":
                next_events,

            "recentEvents":
                recent_events,

            "liveScore":
                live_event
                is not None,

            "liveEvent":
                live_event,

            "liveMessage":
                (
                    None
                    if live_event
                    else (
                        "No verified live match "
                        "is currently available "
                        "for this team."
                    )
                ),

            "source":
                provider_source,

            "providerType":
                provider_type,
        }


    except requests.Timeout:

        return {
            "success":
                False,

            "sport":
                "FOOTBALL",

            "intent":
                intent,

            "query":
                query,

            "error":
                (
                    "Football provider "
                    "request timed out."
                ),

            "source":
                "API-Football",
        }


    except (
        requests.RequestException,
        ValueError,
        RuntimeError,
    ) as error:

        return {
            "success":
                False,

            "sport":
                "FOOTBALL",

            "intent":
                intent,

            "query":
                query,

            "error":
                (
                    "Football service failed: "
                    f"{error}"
                ),

            "source":
                "API-Football",
        }

# =========================================================
# GENERIC SPORTS
# =========================================================

def get_generic_sport_data(
    question: str,
    sport: str,
    intent: str,
    query: str,
) -> dict[str, Any]:

    return {
        "success":
            False,

        "configurationRequired":
            True,

        "sport":
            sport,

        "intent":
            intent,

        "query":
            query,

        "error":
            (
                f"A verified "
                f"{sport.replace('_', ' ').title()} "
                "live/statistics provider "
                "is not configured yet."
            ),

        "fallbackToGeneralAI":
            intent in {
                "GENERAL",
                "DETAILS",
            },

        "source":
            "Sports provider pending",
    }
    
def normalize_generic_game(
    item: dict[str, Any],
    sport: str,
) -> dict[str, Any]:

    league = (
        item.get("league")
        or {}
    )

    country = (
        item.get("country")
        or {}
    )

    teams = (
        item.get("teams")
        or {}
    )

    scores = (
        item.get("scores")
        or {}
    )

    home = (
        teams.get("home")
        or {}
    )

    away = (
        teams.get("away")
        or {}
    )

    home_score = (
        scores.get("home")
    )

    away_score = (
        scores.get("away")
    )

    if isinstance(
        home_score,
        dict,
    ):
        home_score = (
            home_score.get("total")
            or home_score.get("points")
            or home_score.get("score")
        )

    if isinstance(
        away_score,
        dict,
    ):
        away_score = (
            away_score.get("total")
            or away_score.get("points")
            or away_score.get("score")
        )

    status = (
        item.get("status")
        or {}
    )

    if isinstance(
        status,
        dict,
    ):
        status_short = (
            status.get("short")
            or status.get("code")
        )

        status_long = (
            status.get("long")
            or status.get("name")
        )

    else:
        status_short = status
        status_long = status

    return {
        "eventId":
            item.get("id"),

        "event":
            (
                f"{home.get('name') or 'Unknown'} "
                f"vs "
                f"{away.get('name') or 'Unknown'}"
            ),

        "date":
            (
                item.get("date")
                or item.get("datetime")
            ),

        "timestamp":
            item.get("timestamp"),

        "time":
            item.get("time"),

        "timezone":
            item.get("timezone"),

        "league":
            (
                league.get("name")
                if isinstance(league, dict)
                else league
            ),

        "leagueCountry":
            (
                country.get("name")
                if isinstance(country, dict)
                else country
            ),

        "round":
            item.get("round"),

        "sport":
            sport,

        "venue":
            item.get("venue"),

        "venueCity":
            None,

        "status":
            status_short,

        "statusLong":
            status_long,

        "elapsed":
            None,

        "homeTeamId":
            home.get("id"),

        "homeTeam":
            home.get("name"),

        "awayTeamId":
            away.get("id"),

        "awayTeam":
            away.get("name"),

        "homeScore":
            home_score,

        "awayScore":
            away_score,

        "homeWinner":
            None,

        "awayWinner":
            None,
    }
    
def search_generic_team(
    base_url: str,
    query: str,
) -> dict[str, Any] | None:

    payload = (
        api_sports_request(
            base_url,
            "teams",
            {
                "search":
                    query,
            },
        )
    )

    teams = (
        payload.get("response")
        or []
    )

    if not isinstance(
        teams,
        list,
    ):
        return None

    wanted = normalize_text(
        query
    )

    best_team = None
    best_score = -1

    for item in teams:

        if not isinstance(
            item,
            dict,
        ):
            continue

        team = (
            item.get("team")
            or item
        )

        if not isinstance(
            team,
            dict,
        ):
            continue

        name = normalize_text(
            team.get("name")
        )

        country_value = (
            team.get("country")
            or item.get("country")
            or {}
        )

        if isinstance(
            country_value,
            dict,
        ):
            country_name = (
                country_value.get("name")
                or country_value.get("code")
                or ""
            )

        else:
            country_name = str(
                country_value
                or ""
            )

        country = normalize_text(
            country_name
        )

        score = 0

        if name == wanted:
            score += 100

        elif (
            wanted
            and
            name.startswith(
                wanted
            )
        ):
            score += 50

        elif (
            wanted
            and
            wanted in name
        ):
            score += 25

        if (
            wanted == "india"
            and
            country == "india"
        ):
            score += 50

        if score > best_score:

            best_score = score

            best_team = {
                **team,
                "country":
                    country_name,
            }

    return best_team

def get_generic_team_sport_data(
    *,
    sport: str,
    base_url: str,
    query: str,
    intent: str,
) -> dict[str, Any]:

    if not query:

        return {
            "success": False,
            "sport": sport,
            "intent": intent,
            "error": (
                "Please include a team "
                "or country name."
            ),
            "source": "API-Sports",
        }

    current_year = (
        date.today().year
    )

    try:

        team = (
            search_generic_team(
                base_url,
                query,
            )
        )

        if not team:

            return {
                "success": False,
                "sport": sport,
                "intent": intent,
                "query": query,
                "error": (
                    f"{sport.replace('_', ' ').title()} "
                    f"team not found: {query}"
                ),
                "source": "API-Sports",
            }

        team_id = (
            team.get("id")
        )

        if not team_id:

            return {
                "success": False,
                "sport": sport,
                "intent": intent,
                "query": query,
                "error": (
                    "Sports provider returned "
                    "an invalid team."
                ),
                "source": "API-Sports",
            }

        country = (
            team.get("country")
        )

        if isinstance(
            country,
            dict,
        ):

            country = (
                country.get("name")
                or country.get("code")
                or ""
            )

        # =====================================
        # DETAILS / GENERAL
        # =====================================

        if intent in {
            "DETAILS",
            "GENERAL",
        }:

            return {
                "success": True,

                "sport":
                    sport,

                "intent":
                    intent,

                "query":
                    query,

                "team":
                    team.get("name"),

                "teamId":
                    team_id,

                "country":
                    country,

                "league":
                    None,

                "nextEvents":
                    [],

                "recentEvents":
                    [],

                "liveScore":
                    False,

                "liveEvent":
                    None,

                "source":
                    "API-Sports",

                "providerType":
                    (
                        "API-"
                        + sport
                        .replace(
                            "_",
                            " ",
                        )
                        .title()
                    ),
            }

        # =====================================
        # RANKING
        # =====================================

        if intent == "RANKING":

            return {
                "success": False,

                "sport":
                    sport,

                "intent":
                    intent,

                "query":
                    query,

                "team":
                    team.get("name"),

                "country":
                    country,

                "error":
                    (
                        "Please specify the "
                        "league or competition "
                        "for rankings or standings."
                    ),

                "source":
                    "API-Sports",
            }

        # =====================================
        # CURRENT LIVE / SCHEDULE / RESULTS
        # =====================================

        try:

            payload = (
                api_sports_request(
                    base_url,
                    "games",
                    {
                        "team":
                            team_id,

                        "season":
                            current_year,
                    },
                )
            )

        except RuntimeError as error:

            if (
                is_current_season_plan_restricted(
                    error
                )
            ):

                sport_name = (
                    sport
                    .replace(
                        "_",
                        " ",
                    )
                    .title()
                )

                return {
                    "success": False,

                    "sport":
                        sport,

                    "intent":
                        intent,

                    "query":
                        query,

                    "team":
                        team.get("name"),

                    "teamId":
                        team_id,

                    "country":
                        country,

                    "season":
                        current_year,

                    "planRestricted":
                        True,

                    "configurationRequired":
                        False,

                    "fallbackToGeneralAI":
                        False,

                    "error":
                        (
                            f"Current {sport_name} "
                            f"{current_year} match data "
                            "is not available on the "
                            "configured API-Sports "
                            "Free plan."
                        ),

                    "source":
                        "API-Sports",
                }

            raise

        games = (
            payload.get(
                "response"
            )
            or []
        )

        normalized_games = []

        for item in games:

            if not isinstance(
                item,
                dict,
            ):
                continue

            normalized_games.append(
                normalize_generic_game(
                    item,
                    sport.replace(
                        "_",
                        " ",
                    ).title(),
                )
            )

        # =====================================
        # LIVE
        # =====================================

        if intent == "LIVE_SCORE":

            live_statuses = {
                "LIVE",
                "1Q",
                "2Q",
                "3Q",
                "4Q",
                "OT",
                "HT",
                "IN PROGRESS",
                "INPROGRESS",
            }

            live_event = None

            for event in normalized_games:

                status = normalize_text(
                    event.get(
                        "status"
                    )
                ).upper()

                status_long = normalize_text(
                    event.get(
                        "statusLong"
                    )
                ).upper()

                if (
                    status
                    in live_statuses
                    or
                    status_long
                    in live_statuses
                ):

                    live_event = event
                    break

            return {
                "success": True,

                "sport":
                    sport,

                "intent":
                    intent,

                "query":
                    query,

                "team":
                    team.get("name"),

                "teamId":
                    team_id,

                "country":
                    country,

                "league":
                    None,

                "nextEvents":
                    [],

                "recentEvents":
                    [],

                "liveScore":
                    live_event
                    is not None,

                "liveEvent":
                    live_event,

                "liveMessage":
                    (
                        None
                        if live_event
                        else (
                            "No verified live match "
                            "is currently available."
                        )
                    ),

                "source":
                    "API-Sports",

                "providerType":
                    (
                        "API-"
                        + sport
                        .replace(
                            "_",
                            " ",
                        )
                        .title()
                    ),
            }

        # =====================================
        # SCHEDULE
        # =====================================

        if intent == "SCHEDULE":

            upcoming_statuses = {
                "NS",
                "TBD",
                "NOT STARTED",
                "SCHEDULED",
            }

            next_events = []

            for event in normalized_games:

                status = normalize_text(
                    event.get(
                        "status"
                    )
                ).upper()

                status_long = normalize_text(
                    event.get(
                        "statusLong"
                    )
                ).upper()

                if (
                    status
                    in upcoming_statuses
                    or
                    status_long
                    in upcoming_statuses
                ):

                    next_events.append(
                        event
                    )

            next_events.sort(
                key=lambda item: (
                    item.get(
                        "timestamp"
                    )
                    or 0
                )
            )

            return {
                "success": True,

                "sport":
                    sport,

                "intent":
                    intent,

                "query":
                    query,

                "team":
                    team.get("name"),

                "teamId":
                    team_id,

                "country":
                    country,

                "league":
                    None,

                "nextEvents":
                    next_events[:5],

                "recentEvents":
                    [],

                "liveScore":
                    False,

                "liveEvent":
                    None,

                "source":
                    "API-Sports",

                "providerType":
                    (
                        "API-"
                        + sport
                        .replace(
                            "_",
                            " ",
                        )
                        .title()
                    ),
            }

        # =====================================
        # RESULT
        # =====================================

        if intent == "RESULT":

            completed_statuses = {
                "FT",
                "FINISHED",
                "AFTER OT",
                "AFTER PENALTIES",
                "AOT",
            }

            recent_events = []

            for event in normalized_games:

                status = normalize_text(
                    event.get(
                        "status"
                    )
                ).upper()

                status_long = normalize_text(
                    event.get(
                        "statusLong"
                    )
                ).upper()

                if (
                    status
                    in completed_statuses
                    or
                    status_long
                    in completed_statuses
                ):

                    recent_events.append(
                        event
                    )

            recent_events.sort(
                key=lambda item: (
                    item.get(
                        "timestamp"
                    )
                    or 0
                ),
                reverse=True,
            )

            return {
                "success": True,

                "sport":
                    sport,

                "intent":
                    intent,

                "query":
                    query,

                "team":
                    team.get("name"),

                "teamId":
                    team_id,

                "country":
                    country,

                "league":
                    None,

                "nextEvents":
                    [],

                "recentEvents":
                    recent_events[:5],

                "liveScore":
                    False,

                "liveEvent":
                    None,

                "source":
                    "API-Sports",

                "providerType":
                    (
                        "API-"
                        + sport
                        .replace(
                            "_",
                            " ",
                        )
                        .title()
                    ),
            }

        return {
            "success": True,

            "sport":
                sport,

            "intent":
                intent,

            "query":
                query,

            "team":
                team.get("name"),

            "teamId":
                team_id,

            "country":
                country,

            "league":
                None,

            "nextEvents":
                [],

            "recentEvents":
                [],

            "liveScore":
                False,

            "liveEvent":
                None,

            "source":
                "API-Sports",

            "providerType":
                (
                    "API-"
                    + sport
                    .replace(
                        "_",
                        " ",
                    )
                    .title()
                ),
        }

    except requests.Timeout:

        return {
            "success": False,

            "sport":
                sport,

            "intent":
                intent,

            "query":
                query,

            "error":
                (
                    f"{sport.replace('_', ' ').title()} "
                    "provider request timed out."
                ),

            "source":
                "API-Sports",
        }

    except (
        requests.RequestException,
        RuntimeError,
        ValueError,
    ) as error:

        return {
            "success": False,

            "sport":
                sport,

            "intent":
                intent,

            "query":
                query,

            "error":
                (
                    f"{sport.replace('_', ' ').title()} "
                    f"service failed: {error}"
                ),

            "source":
                "API-Sports",
        }
        
def get_formula1_data(
    question: str,
    intent: str,
    query: str,
) -> dict[str, Any]:

    current_year = (
        date.today().year
    )

    try:

        payload = (
            api_sports_request(
                API_FORMULA1_BASE_URL,
                "races",
                {
                    "season":
                        current_year,
                },
            )
        )

        races = (
            payload.get("response")
            or []
        )

        normalized = []

        for item in races[:10]:

            if not isinstance(
                item,
                dict,
            ):
                continue

            competition = (
                item.get("competition")
                or {}
            )

            circuit = (
                item.get("circuit")
                or {}
            )

            normalized.append({
                "eventId":
                    item.get("id"),

                "event":
                    (
                        competition.get("name")
                        or item.get("type")
                        or "Formula 1 race"
                    ),

                "date":
                    item.get("date"),

                "time":
                    item.get("time"),

                "timestamp":
                    None,

                "timezone":
                    None,

                "league":
                    "Formula 1",

                "leagueCountry":
                    competition.get(
                        "location"
                    ),

                "round":
                    item.get("round"),

                "sport":
                    "Formula 1",

                "venue":
                    circuit.get("name"),

                "venueCity":
                    competition.get(
                        "location"
                    ),

                "status":
                    item.get("status"),

                "statusLong":
                    item.get("status"),

                "elapsed":
                    None,

                "homeTeam":
                    None,

                "awayTeam":
                    None,

                "homeScore":
                    None,

                "awayScore":
                    None,
            })

        return {
            "success":
                True,

            "sport":
                "FORMULA_1",

            "intent":
                intent,

            "query":
                query,

            "team":
                None,

            "country":
                None,

            "league":
                "Formula 1",

            "season":
                current_year,

            "nextEvents":
                normalized,

            "recentEvents":
                [],

            "liveScore":
                False,

            "liveEvent":
                None,

            "source":
                "API-Formula-1",

            "providerType":
                "API-Sports",
        }

    except RuntimeError as error:

        error_text = str(
            error
        )

        # Free plan may expose only
        # historical seasons.
        #
        # IMPORTANT:
        # Do NOT silently return 2024
        # as if it were current 2026 data.
        if (
            "Free plans do not have access "
            "to this season"
            in error_text
        ):

            return {
                "success":
                    False,

                "sport":
                    "FORMULA_1",

                "intent":
                    intent,

                "query":
                    query,

                "season":
                    current_year,

                "configurationRequired":
                    False,

                "planRestricted":
                    True,

                "error":
                    (
                        "Current Formula 1 "
                        f"{current_year} data is "
                        "not available on the "
                        "configured API-Sports "
                        "Free plan."
                    ),

                "source":
                    "API-Formula-1",
            }

        return {
            "success":
                False,

            "sport":
                "FORMULA_1",

            "intent":
                intent,

            "query":
                query,

            "error":
                (
                    "Formula 1 service failed: "
                    f"{error}"
                ),

            "source":
                "API-Formula-1",
        }

    except requests.Timeout:

        return {
            "success":
                False,

            "sport":
                "FORMULA_1",

            "intent":
                intent,

            "query":
                query,

            "error":
                (
                    "Formula 1 provider "
                    "request timed out."
                ),

            "source":
                "API-Formula-1",
        }

    except (
        requests.RequestException,
        ValueError,
    ) as error:

        return {
            "success":
                False,

            "sport":
                "FORMULA_1",

            "intent":
                intent,

            "query":
                query,

            "error":
                (
                    "Formula 1 service failed: "
                    f"{error}"
                ),

            "source":
                "API-Formula-1",
        }

# =========================================================
# MAIN CONTROLLER
# =========================================================

def get_sports(
    question: str,
) -> dict[str, Any]:

    sport = detect_sport(
        question
    )

    intent = (
        detect_sports_intent(
            question
        )
    )

    if not sport:

        return {
            "success":
                False,

            "intent":
                intent,

            "error":
                (
                    "Please include a sport, "
                    "team, tournament or "
                    "player name."
                ),

            "fallbackToGeneralAI":
                True,

            "source":
                "Sports router",
        }

    query = (
        clean_sports_query(
            question,
            sport,
        )
    )

    if sport == "FOOTBALL":

        return get_football_data(
            question,
            intent,
            query,
        )

    if sport == "BASKETBALL":

        return get_generic_team_sport_data(
            sport="BASKETBALL",
            base_url=
                API_BASKETBALL_BASE_URL,
            query=query,
            intent=intent,
        )

    if sport == "VOLLEYBALL":

        return get_generic_team_sport_data(
            sport="VOLLEYBALL",
            base_url=
                API_VOLLEYBALL_BASE_URL,
            query=query,
            intent=intent,
        )

    if sport == "HOCKEY":

        if (
            "field hockey"
            in normalize_text(
                question
            )
            or
            "hockey india"
            in normalize_text(
                question
            )
            or
            "హాకీ"
            in normalize_text(
                question
            )
        ):

            return {
                "success": False,

                "sport":
                    "HOCKEY",

                "intent":
                    intent,

                "query":
                    query,

                "configurationRequired":
                    True,

                "error":
                    (
                        "A verified field-hockey "
                        "provider is not configured yet."
                    ),

                "source":
                    "Sports provider pending",
            }

        return get_generic_team_sport_data(
            sport="HOCKEY",

            base_url=
                API_HOCKEY_BASE_URL,

            query=
                query,

            intent=
                intent,
        )

    if sport == "FORMULA_1":

        return get_formula1_data(
            question,
            intent,
            query,
        )

    return get_generic_sport_data(
        question,
        sport,
        intent,
        query,
    )