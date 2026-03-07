"""
Command-line interface for scrapernhl.

Provides easy access to scraping functions directly from the terminal.

Note: Imports are lazy - scrapers are only imported when commands are actually run.
"""

import sys
from datetime import datetime
from pathlib import Path

import click


@click.group()
@click.version_option(package_name="scrapernhl", prog_name="scrapernhl")
def cli():
    """
    ScraperNHL - Command-line interface for multi-league hockey data scraping.

    Scrape NHL, PWHL, AHL, OHL, WHL, and QMJHL data including teams, schedules,
    standings, rosters, stats, and games directly from the command line.
    """
    pass


@cli.command()
@click.option("--output", "-o", help="Output file path (default: nhl_teams.csv)")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["csv", "json", "parquet", "excel"]),
    default="csv",
    help="Output format",
)
@click.option("--polars", is_flag=True, help="Use Polars instead of Pandas")
def teams(output, format, polars):
    """Scrape all NHL teams."""
    from scrapernhl.nhl.scrapers.teams import scrapeTeams

    output_format = "polars" if polars else "pandas"
    click.echo("Scraping NHL teams...")

    try:
        teams_df = scrapeTeams(output_format=output_format)

        if output:
            output_path = Path(output)
        else:
            output_path = Path(f"nhl_teams.{format}")

        _save_dataframe(teams_df, output_path, format, polars)
        click.echo(f"Successfully scraped {len(teams_df)} teams")
        click.echo(f"Saved to: {output_path}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("team")
@click.argument("season")
@click.option("--output", "-o", help="Output file path")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["csv", "json", "parquet", "excel"]),
    default="csv",
    help="Output format",
)
def schedule(team, season, output, format):
    """
    Scrape team schedule.

    TEAM: Team abbreviation (e.g., MTL, TOR, BOS)
    SEASON: Season string (e.g., 20252026)
    """
    from scrapernhl.nhl.scrapers.schedule import scrapeSchedule

    click.echo(f"Scraping {team} schedule for {season}...")

    try:
        schedule_df = scrapeSchedule(team, season)

        if output:
            output_path = Path(output)
        else:
            output_path = Path(f"{team.lower()}_schedule_{season}.{format}")

        _save_dataframe(schedule_df, output_path, format)
        click.echo(f"Successfully scraped {len(schedule_df)} games")
        click.echo(f"Saved to: {output_path}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("date", required=False)
@click.option("--output", "-o", help="Output file path")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["csv", "json", "parquet", "excel"]),
    default="csv",
    help="Output format",
)
def standings(date, output, format):
    """
    Scrape NHL standings.

    DATE: Date in YYYY-MM-DD format (default: today)
    """
    from scrapernhl.nhl.scrapers.standings import scrapeStandings

    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    click.echo(f"Scraping NHL standings for {date}...")

    try:
        standings_df = scrapeStandings(date)

        if output:
            output_path = Path(output)
        else:
            output_path = Path(f"nhl_standings_{date}.{format}")

        _save_dataframe(standings_df, output_path, format)
        click.echo(f"Successfully scraped standings for {len(standings_df)} teams")
        click.echo(f"Saved to: {output_path}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("team")
@click.argument("season")
@click.option("--output", "-o", help="Output file path")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["csv", "json", "parquet", "excel"]),
    default="csv",
    help="Output format",
)
def roster(team, season, output, format):
    """
    Scrape team roster.

    TEAM: Team abbreviation (e.g., MTL, TOR, BOS)
    SEASON: Season string (e.g., 20252026)
    """
    from scrapernhl.nhl.scrapers.roster import scrapeRoster

    click.echo(f"Scraping {team} roster for {season}...")

    try:
        roster_df = scrapeRoster(team, season)

        if output:
            output_path = Path(output)
        else:
            output_path = Path(f"{team.lower()}_roster_{season}.{format}")

        _save_dataframe(roster_df, output_path, format)
        click.echo(f"Successfully scraped {len(roster_df)} players")
        click.echo(f"Saved to: {output_path}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("team")
@click.argument("season")
@click.option("--goalies", is_flag=True, help="Scrape goalie stats instead of skater stats")
@click.option("--session", type=int, default=2, help="Session type (2=regular season, 3=playoffs)")
@click.option("--output", "-o", help="Output file path")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["csv", "json", "parquet", "excel"]),
    default="csv",
    help="Output format",
)
def stats(team, season, goalies, session, output, format):
    """
    Scrape team player statistics.

    TEAM: Team abbreviation (e.g., MTL, TOR, BOS)
    SEASON: Season string (e.g., 20252026)
    """
    from scrapernhl.nhl.scrapers.stats import scrapeTeamStats

    player_type = "goalies" if goalies else "skaters"
    click.echo(f"Scraping {team} {player_type} stats for {season}...")

    try:
        stats_df = scrapeTeamStats(team, season, session=session, goalies=goalies)

        if output:
            output_path = Path(output)
        else:
            output_path = Path(f"{team.lower()}_{player_type}_{season}.{format}")

        _save_dataframe(stats_df, output_path, format)
        click.echo(f"Successfully scraped stats for {len(stats_df)} {player_type}")
        click.echo(f"Saved to: {output_path}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("game_id", type=int)
@click.option("--output", "-o", help="Output file path")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["csv", "json", "parquet", "excel"]),
    default="csv",
    help="Output format",
)
def game(game_id, output, format):
    """
    Scrape play-by-play data for a specific game.

    GAME_ID: NHL game ID (e.g., 2024020001)
    """
    from scrapernhl.nhl.scrapers.games import scrapePlays

    click.echo(f"Scraping play-by-play for game {game_id}...")

    try:
        pbp = scrapePlays(game_id)

        if output:
            output_path = Path(output)
        else:
            output_path = Path(f"game_{game_id}.{format}")

        _save_dataframe(pbp, output_path, format)
        click.echo(f"Successfully scraped {len(pbp)} events")
        click.echo(f"Saved to: {output_path}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("year")
@click.argument("round", required=False, default="all")
@click.option("--output", "-o", help="Output file path")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["csv", "json", "parquet", "excel"]),
    default="csv",
    help="Output format",
)
def draft(year, round, output, format):
    """
    Scrape NHL draft data.

    YEAR: Draft year (e.g., 2024)
    ROUND: Draft round (1-7 or 'all', default: all)
    """
    from scrapernhl.nhl.scrapers.draft import scrapeDraftData

    round_text = f"round {round}" if round != "all" else "all rounds"
    click.echo(f"Scraping {year} NHL draft ({round_text})...")

    try:
        draft_df = scrapeDraftData(year, round)

        if output:
            output_path = Path(output)
        else:
            round_suffix = f"_r{round}" if round != "all" else ""
            output_path = Path(f"nhl_draft_{year}{round_suffix}.{format}")

        _save_dataframe(draft_df, output_path, format)
        click.echo(f"Successfully scraped {len(draft_df)} draft picks")
        click.echo(f"Saved to: {output_path}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# Multi-League Commands
@cli.group()
def pwhl():
    """PWHL (Professional Women's Hockey League) commands."""
    pass


@cli.group()
def ahl():
    """AHL (American Hockey League) commands."""
    pass


@cli.group()
def ohl():
    """OHL (Ontario Hockey League) commands."""
    pass


@cli.group()
def whl():
    """WHL (Western Hockey League) commands."""
    pass


@cli.group()
def qmjhl():
    """QMJHL (Quebec Maritimes Junior Hockey League) commands."""
    pass


# Generic multi-league command factory
def create_league_commands(group, league_name, league_code):
    """Create standard commands for a league using HockeyScraper."""

    @group.command("teams", help=f"Scrape {league_name} teams.")
    @click.option("--season", type=int, help="Season ID")
    @click.option("--output", "-o", help="Output file path")
    @click.option(
        "--format",
        "-f",
        type=click.Choice(["csv", "json", "parquet", "excel"]),
        default="csv",
        help="Output format",
    )
    def league_teams(season, output, format):
        from scrapernhl.client import HockeyScraper

        click.echo(f"Scraping {league_name} teams...")
        try:
            scraper = HockeyScraper(league_code)
            teams_df = scraper.teams_by_season(season=season)

            output_path = Path(output) if output else Path(f"{league_name.lower()}_teams.{format}")
            _save_dataframe(teams_df, output_path, format)
            click.echo(f"Successfully scraped {len(teams_df)} teams")
            click.echo(f"Saved to: {output_path}")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

    @group.command("schedule", help=f"Scrape {league_name} schedule.")
    @click.option("--season", type=int, help="Season ID")
    @click.option("--team-id", type=int, default=-1, help="Team ID (-1 for all teams)")
    @click.option("--output", "-o", help="Output file path")
    @click.option(
        "--format",
        "-f",
        type=click.Choice(["csv", "json", "parquet", "excel"]),
        default="csv",
        help="Output format",
    )
    def league_schedule(season, team_id, output, format):
        from scrapernhl.client import HockeyScraper

        click.echo(f"Scraping {league_name} schedule...")
        try:
            scraper = HockeyScraper(league_code)
            team = "all" if team_id == -1 else str(team_id)
            schedule_df = scraper.schedule(team=team, season=season)

            output_path = (
                Path(output) if output else Path(f"{league_name.lower()}_schedule.{format}")
            )
            _save_dataframe(schedule_df, output_path, format)
            click.echo(f"Successfully scraped {len(schedule_df)} games")
            click.echo(f"Saved to: {output_path}")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

    @group.command("standings", help=f"Scrape {league_name} standings.")
    @click.option("--season", type=int, help="Season ID")
    @click.option("--output", "-o", help="Output file path")
    @click.option(
        "--format",
        "-f",
        type=click.Choice(["csv", "json", "parquet", "excel"]),
        default="csv",
        help="Output format",
    )
    def league_standings(season, output, format):
        from scrapernhl.client import HockeyScraper

        click.echo(f"Scraping {league_name} standings...")
        try:
            scraper = HockeyScraper(league_code)
            standings_df = scraper.standings(season=season)

            output_path = (
                Path(output) if output else Path(f"{league_name.lower()}_standings.{format}")
            )
            _save_dataframe(standings_df, output_path, format)
            click.echo(f"Successfully scraped standings for {len(standings_df)} teams")
            click.echo(f"Saved to: {output_path}")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

    @group.command("roster", help=f"Scrape {league_name} roster for a team.")
    @click.option("--team-id", type=int, required=True, help="Team ID (required)")
    @click.option("--season", type=int, help="Season ID")
    @click.option("--output", "-o", help="Output file path")
    @click.option(
        "--format",
        "-f",
        type=click.Choice(["csv", "json", "parquet", "excel"]),
        default="csv",
        help="Output format",
    )
    def league_roster(team_id, season, output, format):
        from scrapernhl.client import HockeyScraper

        click.echo(f"Scraping {league_name} roster for team {team_id}...")
        try:
            scraper = HockeyScraper(league_code)
            roster_df = scraper.roster(team=str(team_id), season=season)

            output_path = (
                Path(output) if output else Path(f"{league_name.lower()}_roster_{team_id}.{format}")
            )
            _save_dataframe(roster_df, output_path, format)
            click.echo(f"Successfully scraped {len(roster_df)} players")
            click.echo(f"Saved to: {output_path}")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

    @group.command("stats", help=f"Scrape {league_name} player stats.")
    @click.option("--season", type=int, help="Season ID")
    @click.option(
        "--player-type",
        type=click.Choice(["skater", "goalie"]),
        default="skater",
        help="Player type (default: skater)",
    )
    @click.option("--limit", type=int, default=50, help="Number of records to return (default: 50)")
    @click.option("--output", "-o", help="Output file path")
    @click.option(
        "--format",
        "-f",
        type=click.Choice(["csv", "json", "parquet", "excel"]),
        default="csv",
        help="Output format",
    )
    def league_stats(season, player_type, limit, output, format):
        from scrapernhl.client import HockeyScraper

        click.echo(f"Scraping {league_name} {player_type} stats...")
        try:
            scraper = HockeyScraper(league_code)
            position = "goalies" if player_type == "goalie" else "skaters"
            stats_df = scraper.player_stats(season=season, position=position)
            if limit:
                stats_df = stats_df.head(limit)

            output_path = (
                Path(output)
                if output
                else Path(f"{league_name.lower()}_{player_type}_stats.{format}")
            )
            _save_dataframe(stats_df, output_path, format)
            click.echo(f"Successfully scraped stats for {len(stats_df)} {player_type}s")
            click.echo(f"Saved to: {output_path}")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

    @group.command("game", help=f"Scrape {league_name} play-by-play data for a game.")
    @click.argument("game_id", type=int)
    @click.option("--output", "-o", help="Output file path")
    @click.option(
        "--format",
        "-f",
        type=click.Choice(["csv", "json", "parquet", "excel"]),
        default="csv",
        help="Output format",
    )
    def league_game(game_id, output, format):
        from scrapernhl.client import HockeyScraper

        click.echo(f"Scraping {league_name} game {game_id}...")
        try:
            scraper = HockeyScraper(league_code)
            game_df = scraper.play_by_play(game_id)

            output_path = (
                Path(output) if output else Path(f"{league_name.lower()}_game_{game_id}.{format}")
            )
            _save_dataframe(game_df, output_path, format)
            click.echo(f"Successfully scraped {len(game_df)} events")
            click.echo(f"Saved to: {output_path}")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

    @group.command("bootstrap", help=f"Get {league_name} bootstrap/configuration data.")
    @click.option("--season", default="latest", help="Season (default: latest)")
    @click.option("--page-name", default="scorebar", help="Page name context")
    @click.option("--game-id", type=int, help="Optional game ID")
    @click.option("--output", "-o", help="Output file path")
    @click.option(
        "--format",
        "-f",
        type=click.Choice(["json"]),
        default="json",
        help="Output format (JSON only)",
    )
    def league_bootstrap(season, page_name, game_id, output, format):
        import json

        from scrapernhl.client import HockeyScraper

        click.echo(f"Fetching {league_name} bootstrap data...")
        try:
            scraper = HockeyScraper(league_code)
            kwargs = {"season": season, "page_name": page_name}
            if game_id:
                kwargs["game_id"] = game_id

            bootstrap = scraper.bootstrap(**kwargs)

            output_path = (
                Path(output) if output else Path(f"{league_name.lower()}_bootstrap.{format}")
            )
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(bootstrap, f, indent=2)

            click.echo("Successfully fetched bootstrap data")
            click.echo(f"Saved to: {output_path}")

            if "current_league_id" in bootstrap:
                click.echo(f"  League ID: {bootstrap['current_league_id']}")
            if "current_season_id" in bootstrap:
                click.echo(f"  Season ID: {bootstrap['current_season_id']}")
            if "teams" in bootstrap:
                click.echo(f"  Teams: {len(bootstrap['teams'])}")

        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)


# Register league commands
create_league_commands(pwhl, "PWHL", "pwhl")
create_league_commands(ahl, "AHL", "ahl")
create_league_commands(ohl, "OHL", "ohl")
create_league_commands(whl, "WHL", "whl")
create_league_commands(qmjhl, "QMJHL", "qmjhl")


def _save_dataframe(df, path: Path, format: str, is_polars: bool = False):
    """Save DataFrame to file in specified format."""
    path.parent.mkdir(parents=True, exist_ok=True)

    if is_polars:
        # Polars DataFrame
        if format == "csv":
            df.write_csv(str(path))
        elif format == "json":
            df.write_json(str(path))
        elif format == "parquet":
            df.write_parquet(str(path))
        elif format == "excel":
            # Convert to pandas for Excel
            df.to_pandas().to_excel(str(path), index=False, engine="openpyxl")
    else:
        # Pandas DataFrame
        if format == "csv":
            df.to_csv(path, index=False)
        elif format == "json":
            df.to_json(path, orient="records", indent=2)
        elif format == "parquet":
            df.to_parquet(path, index=False)
        elif format == "excel":
            df.to_excel(path, index=False, engine="openpyxl")


if __name__ == "__main__":
    cli()
