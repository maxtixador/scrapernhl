# scrapernhl/enrichment.py
"""
HockeyTech DataFrame enrichment helpers.

Each function takes a raw DataFrame and a bootstrap subtree, adds
league/season metadata and human-readable columns, and returns the
enriched DataFrame.
"""

import numpy as np
import pandas as pd

from .config import month_mapping, month_start_end_mapping

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _season_meta(season_bootstrap: dict, season: int) -> tuple[str | None, int | None, str | None]:
    """Return (seasonName, seasonStartYear, seasonEndYear) for *season*."""
    seasons = season_bootstrap.get("seasons", [])
    if not seasons:
        seasons = (
            season_bootstrap.get("regularSeasons", [])
            + season_bootstrap.get("playoffSeasons", [])
        )
    seasons_df = pd.json_normalize(seasons)
    seasons_dict = seasons_df.set_index("id").to_dict(orient="index") if not seasons_df.empty else {}

    season_name: str | None = seasons_dict.get(str(season), {}).get("name")
    season_start_year: int | None = int(season_name[:4]) if season_name else None
    season_end_year: str | None = str(season_start_year + 1) if season_start_year else None
    return season_name, season_start_year, season_end_year


def _teams_dict(season_bootstrap: dict, index_by: str = "team_code") -> dict:
    """Return a dict keyed by *index_by* from the bootstrap teams list."""
    teams = season_bootstrap.get("teamsNoAll", season_bootstrap.get("teams", []))
    if not teams:
        return {}
    teams_df = pd.json_normalize(teams)
    return teams_df.set_index(index_by).to_dict(orient="index")


def _split_name(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add firstName / lastName columns from the 'name' column.

    Handles both "LastName, FirstName" (HockeyTech) and
    "FirstName LastName" (PWHL) formats.
    """
    name_parts = df["name"].str.split(", ", n=1, expand=True)
    if len(name_parts.columns) == 2:
        df[["lastName", "firstName"]] = name_parts
    else:
        name_parts = df["name"].str.split(" ", n=1, expand=True)
        if len(name_parts.columns) == 2:
            df[["firstName", "lastName"]] = name_parts
        else:
            df["firstName"] = df["name"]
            df["lastName"] = None
    return df


# ---------------------------------------------------------------------------
# Public enrichment functions
# ---------------------------------------------------------------------------

def enrich_stats(df: pd.DataFrame, season_bootstrap: dict, season: int, league: str) -> pd.DataFrame:
    """Enrich a HockeyTech player-stats DataFrame."""
    teams_dict = _teams_dict(season_bootstrap, index_by="team_code")
    season_name, season_start_year, season_end_year = _season_meta(season_bootstrap, season)

    if "name" not in df.columns and "shortname" in df.columns:
        df["name"] = df["shortname"]
    if "name" in df.columns:
        df = _split_name(df)
        df["playerName"] = df["name"]
    df["teamId"] = df["team_code"].map(lambda x: teams_dict.get(x, {}).get("id"))
    df["teamLogo"] = df["team_code"].map(lambda x: teams_dict.get(x, {}).get("logo"))
    df["season"] = str(season)
    df["league"] = league
    df["seasonName"] = season_name
    df["seasonStartYear"] = season_start_year
    df["seasonEndYear"] = season_end_year

    cols_rename = {
        "jersey_number": "jerseyNumber",
        "team_code": "teamCode",
        "games_played": "GP",
        "goals": "G",
        "shots": "S",
        "shooting_percentage": "Sh%",
        "assists": "A",
        "points": "PTS",
        "plus_minus": "+/-",
        "penalty_minutes": "PIM",
        "points_per_game": "PTS/GP",
        "penalty_minutes_per_game": "PIM/GP",
        "power_play_goals": "PPG",
        "power_play_assists": "PPA",
        "short_handed_goals": "SHG",
        "short_handed_assists": "SHA",
        "game_winning_goals": "GWG",
        "shootout_goals": "SG",
    }
    df = df.rename(columns=cols_rename)

    num_cols = [
        "GP", "GWG", "G", "S", "Sh%", "A", "PTS", "PPG", "+/-",
        "PIM", "PIM/GP", "PTS/GP", "PPA", "SHG", "SHA", "SG", "rank",
    ]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def enrich_schedule(df: pd.DataFrame, season_bootstrap: dict, season: int, league: str) -> pd.DataFrame:
    """Enrich a HockeyTech schedule DataFrame (after _format_hockeytech_schedule)."""
    teams_dict = _teams_dict(season_bootstrap, index_by="id")

    seasons = season_bootstrap.get("seasons", [])
    if not seasons:
        seasons = (
            season_bootstrap.get("regularSeasons", [])
            + season_bootstrap.get("playoffSeasons", [])
        )
    seasons_df = pd.json_normalize(seasons)
    seasons_dict = seasons_df.set_index("id").to_dict(orient="index") if not seasons_df.empty else {}

    season_name: str | None = seasons_dict.get(str(season), {}).get("name")
    season_start_date: str | None = seasons_dict.get(str(season), {}).get("start_date")
    if season_start_date:
        season_start_year: int | None = int(season_start_date[:4])
    elif season_name and season_name[:4].isdigit():
        season_start_year = int(season_name[:4])
    else:
        season_start_year = None
    season_end_year: str | None = str(season_start_year + 1) if season_start_year else None

    df["homeTeam"] = df["homeId"].map(lambda x: teams_dict.get(x, {}).get("name"))
    df["awayTeam"] = df["awayId"].map(lambda x: teams_dict.get(x, {}).get("name"))
    df["homeCode"] = df["homeId"].map(lambda x: teams_dict.get(x, {}).get("team_code"))
    df["awayCode"] = df["awayId"].map(lambda x: teams_dict.get(x, {}).get("team_code"))
    df["homeDivision"] = df["homeId"].map(lambda x: teams_dict.get(x, {}).get("division_id"))
    df["awayDivision"] = df["awayId"].map(lambda x: teams_dict.get(x, {}).get("division_id"))
    df["homeLogo"] = df["homeId"].map(lambda x: teams_dict.get(x, {}).get("logo"))
    df["awayLogo"] = df["awayId"].map(lambda x: teams_dict.get(x, {}).get("logo"))
    df["season"] = str(season)
    df["league"] = league
    df["seasonName"] = season_name
    df["seasonStartDate"] = season_start_date
    df["seasonStartYear"] = season_start_year
    df["seasonEndYear"] = season_end_year

    df["dayOfWeek"] = df["date"].map(lambda x: x[:3] if x else None)
    df["monthText"] = df["date"].map(lambda x: x[5:8] if x else None)
    df["monthNum"] = df["monthText"].map(month_mapping)
    df["day"] = df["date"].map(lambda x: x.split()[-1].zfill(2) if x else None)
    df["year"] = df["monthText"].map(
        lambda x: season_start_year
        if x in month_start_end_mapping.get("seasonStartYear", {})
        else season_end_year
    )
    df = df.rename(columns={"date": "dateString"})
    df["date"] = pd.to_datetime(
        df.apply(
            lambda row: (
                f"{row['year']}-{row['monthNum']}-{row['day']}"
                if row["year"] and row["monthNum"] and row["day"]
                else None
            ),
            axis=1,
        ),
        errors="coerce",
        format="%Y-%m-%d",
    )
    return df


def enrich_roster(df: pd.DataFrame, season_bootstrap: dict, season: int, league: str, team: str) -> pd.DataFrame:
    """Enrich a HockeyTech roster DataFrame."""
    teams_dict = _teams_dict(season_bootstrap, index_by="id")
    season_name, season_start_year, season_end_year = _season_meta(season_bootstrap, season)

    df = _split_name(df)
    try:
        df["teamId"] = int(team)
    except (TypeError, ValueError):
        df["teamId"] = None
    df["teamName"] = teams_dict.get(str(team), {}).get("name")
    df["teamCode"] = teams_dict.get(str(team), {}).get("team_code")
    df["teamLogo"] = teams_dict.get(str(team), {}).get("logo")
    df["season"] = str(season)
    df["league"] = league
    df["seasonName"] = season_name
    df["seasonStartYear"] = season_start_year
    df["seasonEndYear"] = season_end_year

    # Birthplace
    location_field = "hometown" if "hometown" in df.columns else "birthplace"
    if location_field in df.columns:
        split_cols = df[location_field].str.split(", ", n=2, expand=True)
        num_split_cols = len(split_cols.columns)
        df["n_birthplace"] = split_cols.notna().sum(axis=1)

        mask_2 = df["n_birthplace"] == 2
        if mask_2.any() and num_split_cols >= 2:
            df.loc[mask_2, ["birthCity", "birthCountry"]] = split_cols.loc[mask_2, [0, 1]].values

        mask_3 = df["n_birthplace"] == 3
        if mask_3.any() and num_split_cols >= 3:
            df.loc[mask_3, ["birthCity", "birthState", "birthCountry"]] = split_cols.loc[mask_3, [0, 1, 2]].values

    # Height
    if "h" in df.columns:
        height_parts = df["h"].str.extract(r"(?P<feet>\d+)(?:\D+(?P<inches>\d+))?")
        feet = pd.to_numeric(height_parts["feet"], errors="coerce")
        inches = pd.to_numeric(height_parts["inches"], errors="coerce").fillna(0)
        df["height_cm"] = (feet * 12 + inches) * 2.54

    # Shoots / catches
    if "catches" in df.columns and "shoots" in df.columns and "position" in df.columns:
        df["shootsCatches"] = df["catches"].where(df["position"] == "G", df["shoots"])

    return df


def enrich_standings(df: pd.DataFrame, season_bootstrap: dict, season: int, league: str) -> pd.DataFrame:
    """Enrich a HockeyTech standings DataFrame."""
    teams_dict = _teams_dict(season_bootstrap, index_by="team_code")
    season_name, season_start_year, season_end_year = _season_meta(season_bootstrap, season)

    split = df["team_code"].str.split(" - ", n=1, expand=True)
    if split.shape[1] == 2:
        df["prefixTeam"] = split[0]
        df["team_code"] = split[1].where(split[1].notna(), split[0])
        df["prefixTeam"] = np.where(df["team_code"] == df["prefixTeam"], None, df["prefixTeam"])
    else:
        df["prefixTeam"] = None
    df["team_code"] = df["team_code"].str.replace(".", "", regex=False)

    df["season"] = str(season)
    df["league"] = league
    df["seasonName"] = season_name
    df["seasonStartYear"] = season_start_year
    df["seasonEndYear"] = season_end_year
    df["teamId"] = df["team_code"].map(lambda x: teams_dict.get(x, {}).get("id"))
    df["teamName"] = df["team_code"].map(lambda x: teams_dict.get(x, {}).get("name"))
    df["teamLogo"] = df["team_code"].map(lambda x: teams_dict.get(x, {}).get("logo"))

    return df
