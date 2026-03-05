# scrapernhl/parsers.py
"""Response parsers: extract the relevant list/dict from each API response."""

from .utils import extract_nested


def parse_pbp(league: str, pbp_style: str, data: dict) -> list:
    if league == "nhl":
        return data.get("plays", [])

    if pbp_style == "hockeytech_a":
        raw = data if isinstance(data, list) else []
        return [_unpack_hockeytech_a_event(ev) for ev in raw]

    return extract_nested(data, ["GC", "Pxpverbose"])


def _unpack_hockeytech_a_event(ev: dict) -> dict:
    """Flatten the 'details' sub-dict of an AHL/PWHL PBP event into the top level.

    The gameCenterPlayByPlay feed wraps every per-event field inside a 'details'
    key.  Unpacking it here keeps all downstream transform logic league-agnostic.
    """
    flat = {"event": ev.get("event")}
    details = ev.get("details") or {}

    # Period: details.period is a dict like {"id": "1", "shortName": "1", "longName": "1st"}
    period_obj = details.get("period") or {}
    flat["period"] = period_obj.get("id")  # "1", "2", "3", "4" …

    # Time elapsed in the period (MM:SS string)
    flat["time"] = details.get("time")

    # Shooter / goalie / scorer player objects (dicts with id, firstName, lastName …)
    for player_field in ("shooter", "goalie", "scorer", "scoredBy"):
        if player_field in details:
            flat[player_field] = details[player_field]

    # Coordinates — API uses camelCase; normalise to snake_case used downstream
    flat["x_location"] = details.get("xLocation")
    flat["y_location"] = details.get("yLocation")

    # On-ice arrays
    flat["plus"] = details.get("plus_players") or details.get("plusPlayers") or []
    flat["minus"] = details.get("minus_players") or details.get("minusPlayers") or []

    # Home / away scoring team (derive from team id vs home/away context if present)
    flat["team_id"] = (details.get("team") or {}).get("id")

    # Strength / goal properties
    props = details.get("properties") or {}
    is_pp = bool(props.get("isPowerPlay"))
    is_sh = bool(props.get("isShortHanded"))
    is_en = bool(props.get("isEmptyNet"))
    strength = "PP" if is_pp else "SH" if is_sh else "EV"
    flat["goal_type"] = f"{strength}.EN" if is_en else strength
    flat["isGoal"] = details.get("isGoal", False)

    # Shot quality / type (for shot events)
    flat["shotQuality"] = details.get("shotQuality")
    flat["shotType"] = details.get("shotType")

    # Penalty fields
    flat["game_penalty_id"] = details.get("game_penalty_id")
    flat["against_team_id"] = (details.get("againstTeam") or {}).get("id")

    # Preserve any remaining detail fields not explicitly mapped
    skip = {"period", "time", "shooter", "goalie", "scorer", "scoredBy",
            "xLocation", "yLocation", "plus_players", "minus_players",
            "plusPlayers", "minusPlayers", "team", "properties",
            "isGoal", "shotQuality", "shotType", "game_penalty_id", "againstTeam"}
    for k, v in details.items():
        if k not in skip and k not in flat:
            flat[k] = v

    return flat


def parse_stats(league: str, data: dict, position: str) -> list:
    if league == "nhl":
        return data.get("goalies" if position == "goalies" else "skaters", [])

    if isinstance(data, dict):
        players = extract_nested(data, ["SiteKit", "Players"])
        return players if players else data.get("players", [])

    if isinstance(data, list) and data and "sections" in data[0]:
        players = []
        for section in data[0].get("sections", []):
            for item in section.get("data", []):
                if "row" in item:
                    players.append(item["row"])
        return players

    return data if isinstance(data, list) else []


def parse_schedule(league: str, data: dict) -> list:
    if league == "nhl":
        return data.get("games", [])
    return data[0].get("sections", [])[0].get("data", [])


def parse_roster(league: str, data: dict) -> list:
    if league == "nhl":
        roster = []
        roster.extend(data.get("forwards", []))
        roster.extend(data.get("defensemen", []))
        roster.extend(data.get("goalies", []))
        return roster

    roster_data = data.get("roster", [])
    if isinstance(roster_data, list) and roster_data and "sections" in roster_data[0]:
        players = []
        for section in roster_data[0].get("sections", []):
            title = section.get("title", "").lower()
            if title not in ["forwards", "defencemen", "defenders", "goalies"]:
                continue
            for item in section.get("data", []):
                if "row" in item:
                    players.append(item["row"])
        return players

    return extract_nested(data, ["SiteKit", "Roster"])


def parse_player_page(data: dict) -> dict:
    """Extract the SiteKit subtree from a HockeyTech player page response.

    Returns a dict with keys like 'info', 'careerStats', 'seasonStats', 'gameByGame'.
    """
    if isinstance(data, dict):
        return data.get("SiteKit", data)
    return {}


def parse_standings(league: str, data: dict) -> list:
    if league == "nhl":
        return data.get("standings", [])

    if isinstance(data, list) and data and "sections" in data[0]:
        teams = []
        for section in data[0].get("sections", []):
            for item in section.get("data", []):
                if "row" in item:
                    teams.append(item["row"])
        return teams

    return extract_nested(data, ["SiteKit", "Standings"])
