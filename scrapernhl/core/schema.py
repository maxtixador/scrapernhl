"""
schema.py : Column standardization and data validation for NHL data.

This module defines standard column schemas for all data types scraped from NHL APIs.
All scrapers should use these schemas to ensure consistency across the package.

Example:
    >>> from scrapernhl.core.schema import standardize_columns, validate_data_quality
    >>> 
    >>> # Standardize columns
    >>> df = scrapeTeams()
    >>> df = standardize_columns(df, "teams", strict=True)
    >>> 
    >>> # Check data quality
    >>> metrics = validate_data_quality(df, "teams")
    >>> print(f"Completeness: {metrics['completeness']:.1%}")
"""

from typing import Dict, List, Optional, Set, Union
from dataclasses import dataclass, field
import pandas as pd
from scrapernhl.core.logging_config import get_logger

LOG = get_logger(__name__)


@dataclass
class ColumnSchema:
    """
    Defines expected columns for a data type.
    
    Attributes:
        required: Columns that must exist
        optional: Columns that may exist
        rename_map: Maps API column names to standard names
        dtypes: Expected data types for columns
    
    Example:
        >>> schema = ColumnSchema(
        ...     required={"id", "name"},
        ...     optional={"description"},
        ...     rename_map={"fullName": "name"},
        ...     dtypes={"id": "int64", "name": "string"}
        ... )
    """
    required: Set[str] = field(default_factory=set)
    optional: Set[str] = field(default_factory=set)
    rename_map: Dict[str, str] = field(default_factory=dict)
    dtypes: Dict[str, str] = field(default_factory=dict)


# Standard column schemas for each data type
SCHEMAS = {
    "teams": ColumnSchema(
        required={"id", "triCode"},
        optional={"name", "fullName", "placeName", "commonName", "division", "conference", "franchiseId"},
        rename_map={
            "placeName.default": "placeName",
            "commonName.default": "commonName",
            "name.default": "fullName",
            "abbrev": "triCode",
        },
        dtypes={
            "id": "int64",
            "franchiseId": "int64",
            "triCode": "string",
            "fullName": "string",
        }
    ),
    
    "schedule": ColumnSchema(
        required={"id", "gameDate", "homeTeam", "awayTeam", "gameState"},
        optional={"venue", "startTimeUTC", "gameType", "season"},
        rename_map={
            "homeTeam.id": "homeTeamId",
            "homeTeam.abbrev": "homeTeamAbbrev",
            "awayTeam.id": "awayTeamId",
            "awayTeam.abbrev": "awayTeamAbbrev",
        },
        dtypes={
            "id": "int64",
            "gameDate": "string",
            "homeTeamId": "int64",
            "awayTeamId": "int64",
        }
    ),
    
    "standings": ColumnSchema(
        required={"teamName", "wins", "losses", "points", "gamesPlayed"},
        optional={"goalFor", "goalAgainst", "goalDifferential", "regulationWins", "teamAbbrev"},
        rename_map={
            "teamName.default": "teamName",
            "teamAbbrev.default": "teamAbbrev",
        },
        dtypes={
            "wins": "int64",
            "losses": "int64",
            "points": "int64",
            "gamesPlayed": "int64",
        }
    ),
    
    "roster": ColumnSchema(
        required={"id", "firstName", "lastName", "sweaterNumber", "positionCode"},
        optional={"heightInInches", "weightInPounds", "shootsCatches", "birthDate", "fullName"},
        rename_map={
            "firstName.default": "firstName",
            "lastName.default": "lastName",
        },
        dtypes={
            "id": "int64",
            "sweaterNumber": "int64",
            "heightInInches": "int64",
            "weightInPounds": "int64",
        }
    ),
    
    "plays": ColumnSchema(
        required={"eventId", "period", "timeInPeriod", "typeDescKey", "situationCode"},
        optional={"xCoord", "yCoord", "details", "homeTeamDefendingSide"},
        rename_map={
            "periodDescriptor.number": "period",
            "timeInPeriod": "timeInPeriod",
            "typeDescKey": "eventType",
            "details.xCoord": "xCoord",
            "details.yCoord": "yCoord",
        },
        dtypes={
            "eventId": "int64",
            "period": "int64",
            "xCoord": "float64",
            "yCoord": "float64",
        }
    ),
    
    "game_pbp": ColumnSchema(
        required={"gameId", "Event", "Per", "timeInPeriodSec", "Tm"},
        optional={"x", "y", "player1Id", "player2Id", "player3Id", "Str", "scoreDiff"},
        rename_map={},
        dtypes={
            "gameId": "int64",
            "Per": "int64",
            "timeInPeriodSec": "int64",
            "elapsedTime": "int64",
            "scoreDiff": "int64",
            "x": "float64",
            "y": "float64",
        }
    ),
    
    "shifts": ColumnSchema(
        required={"playerId", "period", "startTime", "endTime", "duration"},
        optional={"shiftNumber", "teamId", "teamAbbrev", "firstName", "lastName"},
        rename_map={
            "firstName.default": "firstName",
            "lastName.default": "lastName",
        },
        dtypes={
            "playerId": "int64",
            "period": "int64",
            "shiftNumber": "int64",
            "duration": "int64",
        }
    ),
}


def standardize_columns(
    df: pd.DataFrame,
    schema_name: str,
    strict: bool = False,
    warn_missing: bool = True
) -> pd.DataFrame:
    """
    Standardize DataFrame columns according to schema.
    
    Args:
        df: DataFrame to standardize
        schema_name: Name of schema to apply (e.g., "teams", "schedule")
        strict: If True, raise error for missing required columns
        warn_missing: If True, log warnings for missing optional columns
    
    Returns:
        Standardized DataFrame with renamed columns and correct dtypes
    
    Raises:
        ValueError: If strict=True and required columns are missing
    
    Example:
        >>> df = scrapeTeams()
        >>> df = standardize_columns(df, "teams", strict=True)
        >>> # df now has standardized column names and types
    """
    from scrapernhl.exceptions import DataValidationError
    
    if schema_name not in SCHEMAS:
        LOG.warning(f"Unknown schema '{schema_name}', returning unchanged DataFrame")
        return df
    
    schema = SCHEMAS[schema_name]
    df = df.copy()
    
    # Apply column renaming
    if schema.rename_map:
        # Only rename columns that exist
        rename = {k: v for k, v in schema.rename_map.items() if k in df.columns}
        if rename:
            df = df.rename(columns=rename)
            LOG.debug(f"Renamed columns for {schema_name}: {list(rename.values())}")
    
    # Check required columns
    missing_required = schema.required - set(df.columns)
    if missing_required:
        msg = f"Missing required columns for {schema_name}: {sorted(missing_required)}"
        if strict:
            raise DataValidationError(msg, missing_columns=list(missing_required))
        else:
            LOG.warning(msg)
    
    # Check optional columns (if warn_missing)
    if warn_missing:
        missing_optional = schema.optional - set(df.columns)
        if missing_optional:
            LOG.debug(f"Missing optional columns for {schema_name}: {sorted(missing_optional)}")
    
    # Apply dtypes
    for col, dtype in schema.dtypes.items():
        if col in df.columns:
            try:
                df[col] = df[col].astype(dtype)
            except (ValueError, TypeError) as e:
                LOG.warning(f"Could not convert {col} to {dtype}: {e}")
    
    return df


def validate_data_quality(
    df: pd.DataFrame, 
    schema_name: str
) -> Dict[str, Union[int, float, List[str], Dict[str, int]]]:
    """
    Analyze data quality metrics for a DataFrame.
    
    Args:
        df: DataFrame to analyze
        schema_name: Schema name for context
    
    Returns:
        Dictionary with quality metrics:
            - schema: Schema name
            - total_rows: Number of rows
            - total_columns: Number of columns
            - missing_values: Dict of {column: count} for columns with missing values
            - duplicate_rows: Number of duplicate rows
            - completeness: Percentage of non-null values (0.0 to 1.0)
            - empty_strings: Columns with empty string values
    
    Example:
        >>> df = scrapeTeams()
        >>> metrics = validate_data_quality(df, "teams")
        >>> print(f"Data completeness: {metrics['completeness']:.1%}")
        >>> if metrics['duplicate_rows'] > 0:
        ...     print(f"Warning: {metrics['duplicate_rows']} duplicate rows")
    """
    metrics = {
        "schema": schema_name,
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_values": {},
        "duplicate_rows": int(df.duplicated().sum()),
        "completeness": 0.0,
        "empty_strings": [],
    }
    
    # Missing values per column
    missing = df.isna().sum()
    metrics["missing_values"] = {col: int(count) for col, count in missing.items() if count > 0}
    
    # Overall completeness
    total_cells = df.size
    if total_cells > 0:
        non_null_cells = df.notna().sum().sum()
        metrics["completeness"] = float(non_null_cells / total_cells)
    
    # Empty strings in object columns
    for col in df.select_dtypes(include=['object', 'string']).columns:
        if (df[col] == "").any():
            metrics["empty_strings"].append(col)
    
    return metrics


def log_data_quality(
    df: pd.DataFrame, 
    schema_name: str, 
    level: str = "INFO"
) -> None:
    """
    Log data quality metrics.
    
    Args:
        df: DataFrame to analyze
        schema_name: Schema name for context
        level: Logging level ("DEBUG", "INFO", "WARNING", "ERROR")
    
    Example:
        >>> df = scrapeTeams()
        >>> log_data_quality(df, "teams", level="INFO")
        # Logs: Data Quality Report for teams:
        #   Rows: 32, Columns: 8
        #   Completeness: 98.5%
        #   Duplicate rows: 0
    """
    metrics = validate_data_quality(df, schema_name)
    
    log_func = getattr(LOG, level.lower())
    log_func(f"Data Quality Report for {schema_name}:")
    log_func(f"  Rows: {metrics['total_rows']}, Columns: {metrics['total_columns']}")
    log_func(f"  Completeness: {metrics['completeness']:.1%}")
    log_func(f"  Duplicate rows: {metrics['duplicate_rows']}")
    
    if metrics['missing_values']:
        log_func(f"  Missing values: {metrics['missing_values']}")
    
    if metrics['empty_strings']:
        log_func(f"  Empty strings in: {metrics['empty_strings']}")


def validate_game_id(game_id: Union[int, str]) -> int:
    """
    Validate and normalize NHL game ID.
    
    Args:
        game_id: Game ID to validate (int or string)
    
    Returns:
        Validated game ID as integer
    
    Raises:
        InvalidGameError: If game ID format is invalid
    
    Example:
        >>> validate_game_id(2024020001)  # Valid
        2024020001
        >>> validate_game_id("2024020001")  # Valid string
        2024020001
        >>> validate_game_id(123)  # Invalid - too short
        InvalidGameError: Invalid game ID format: 123
    """
    from scrapernhl.exceptions import InvalidGameError
    
    try:
        game_id_int = int(game_id)
    except (ValueError, TypeError):
        raise InvalidGameError(f"Game ID must be integer or numeric string: {game_id}")
    
    # NHL game IDs are 10 digits: SSSSTTGGGG
    # SSSS = season (e.g., 2024)
    # TT = game type (01=preseason, 02=regular, 03=playoff, 04=all-star)
    # GGGG = game number (0001-9999)
    if game_id_int < 2000000000 or game_id_int > 2099999999:
        raise InvalidGameError(
            f"Invalid game ID format: {game_id}. "
            f"Expected 10-digit format: SSSSTTGGGG (e.g., 2024020001)"
        )
    
    return game_id_int


def validate_season(season: str) -> str:
    """
    Validate and normalize NHL season string.
    
    Args:
        season: Season string (e.g., "20242025")
    
    Returns:
        Validated season string
    
    Raises:
        InvalidSeasonError: If season format is invalid
    
    Example:
        >>> validate_season("20242025")  # Valid
        '20242025'
        >>> validate_season("2024-2025")  # Invalid format
        InvalidSeasonError: Invalid season format: 2024-2025
    """
    from scrapernhl.exceptions import InvalidSeasonError
    
    if not isinstance(season, str):
        raise InvalidSeasonError(f"Season must be string: {season}")
    
    # Remove any separators (-, /)
    season_clean = season.replace("-", "").replace("/", "")
    
    # Check format: YYYYYYYY (8 digits)
    if len(season_clean) != 8:
        raise InvalidSeasonError(
            f"Invalid season format: {season}. "
            f"Expected 8-digit format: YYYYYYYY (e.g., 20242025)"
        )
    
    try:
        start_year = int(season_clean[:4])
        end_year = int(season_clean[4:])
    except ValueError:
        raise InvalidSeasonError(f"Season must contain only digits: {season}")
    
    # Check that end year is start year + 1
    if end_year != start_year + 1:
        raise InvalidSeasonError(
            f"Invalid season: {season}. End year must be start year + 1"
        )
    
    # Check reasonable range (NHL founded 1917)
    if start_year < 1917 or start_year > 2100:
        raise InvalidSeasonError(f"Season year out of range: {season}")
    
    return season_clean


def get_schema(schema_name: str) -> Optional[ColumnSchema]:
    """
    Get a column schema by name.
    
    Args:
        schema_name: Name of schema (e.g., "teams", "schedule")
    
    Returns:
        ColumnSchema object or None if not found
    
    Example:
        >>> schema = get_schema("teams")
        >>> print(f"Required columns: {schema.required}")
    """
    return SCHEMAS.get(schema_name)


def list_schemas() -> List[str]:
    """
    List all available schema names.
    
    Returns:
        List of schema names
    
    Example:
        >>> schemas = list_schemas()
        >>> print(f"Available schemas: {', '.join(schemas)}")
    """
    return list(SCHEMAS.keys())
