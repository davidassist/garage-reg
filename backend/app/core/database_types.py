"""
Adatbázis típusok és utilities SQLite kompatibilitáshoz
"""
from sqlalchemy import JSON, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects import sqlite

# JSON type ami SQLite-ban is működik
def get_json_type():
    """
    Visszaadja a megfelelő JSON típust az adatbázis engine-hez
    - PostgreSQL-ben JSONB
    - SQLite-ban JSON (vagy Text)
    """
    return JSON

# JSONB replacement SQLite-hoz
class SQLiteJSON(sqlite.JSON):
    """SQLite-hoz optimalizált JSON típus"""
    pass

# Universal JSON column factory
def create_json_column(**kwargs):
    """
    Platform független JSON oszlop
    """
    return JSON(**kwargs)