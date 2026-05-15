import os
import re
from functools import lru_cache

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool

load_dotenv()


def _get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not set. Configure it in environment variables."
        )
    return database_url


def _is_neon_pooler_url(database_url: str) -> bool:
    return "pooler" in database_url


def _get_target_schema() -> str:
    schema = os.getenv("DB_SCHEMA") or os.getenv("DBT_SCHEMA") or "public"
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", schema):
        raise RuntimeError(
            "Invalid schema name in DB_SCHEMA/DBT_SCHEMA environment variable."
        )
    return schema


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    database_url = _get_database_url()
    engine_kwargs = {
        "poolclass": QueuePool,
        "pool_size": 3,
        "max_overflow": 2,
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    if not _is_neon_pooler_url(database_url):
        engine_kwargs["connect_args"] = {"options": "-c statement_timeout=30000"}

    return create_engine(
        database_url,
        **engine_kwargs,
    )


def run_query(sql: str, params: dict | None = None) -> pd.DataFrame:
    with get_engine().connect() as connection:
        schema = _get_target_schema()
        connection.execute(text(f'SET search_path TO "{schema}", public'))
        return pd.read_sql_query(text(sql), con=connection, params=params or {})
