"""
Formula 1 Race Analytics - Data Ingestion Pipeline
EAS 550 - DMQL | Team: Karisha, Swaminathan, Vishal
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from psycopg2.extras import execute_values

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable is not set.")
    sys.exit(1)

CSV_DIR = os.environ.get("CSV_DIR", "./data")

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=3,
    max_overflow=2,
    pool_recycle=300,
    pool_pre_ping=True,
    connect_args={"options": "-c statement_timeout=30000"},
)


def clean_column(series: pd.Series, target_type: str = "str") -> pd.Series:
    series = series.replace({"\\N": None, "": None})

    if target_type == "int":
        return pd.to_numeric(series, errors="coerce").astype("Int64")
    elif target_type == "float":
        return pd.to_numeric(series, errors="coerce").astype("Float64")
    elif target_type == "date":
        return pd.to_datetime(series, errors="coerce").dt.date
    elif target_type == "time":
        return series
    else:
        return series


def read_csv(filename: str) -> pd.DataFrame:
    filepath = os.path.join(CSV_DIR, filename)
    if not os.path.exists(filepath):
        logger.warning(f"File not found: {filepath}. Skipping.")
        return pd.DataFrame()
    df = pd.read_csv(filepath, encoding="utf-8", na_values=["\\N", ""])
    logger.info(f"Read {filename}")
    return df


def upsert_dataframe(df: pd.DataFrame, table_name: str, conflict_columns: list):
    if df.empty:
        logger.warning(f"No data to insert for table '{table_name}'. Skipping.")
        return

    cols = df.columns.tolist()
    col_list = ", ".join(cols)
    conflict_list = ", ".join(conflict_columns)

    sql = f"""
        INSERT INTO {table_name} ({col_list})
        VALUES %s
        ON CONFLICT ({conflict_list}) DO NOTHING
    """

    def convert(v):
        if pd.isna(v):
            return None
        if isinstance(v, (np.integer,)):
            return int(v)
        if isinstance(v, (np.floating,)):
            return float(v)
        return v

    records = [
        tuple(convert(v) for v in row)
        for row in df.itertuples(index=False, name=None)
    ]

    BATCH_SIZE = 5000
    conn = engine.raw_connection()
    try:
        cur = conn.cursor()
        for i in range(0, len(records), BATCH_SIZE):
            batch = records[i:i + BATCH_SIZE]
            execute_values(cur, sql, batch, page_size=BATCH_SIZE)
        conn.commit()
        cur.close()
    finally:
        conn.close()

    logger.info(f"Upserted into '{table_name}'.")


def ingest_seasons():
    df = read_csv("seasons.csv")
    if df.empty:
        return
    df.columns = ["year", "url"]
    df["year"] = clean_column(df["year"], "int")
    upsert_dataframe(df, "seasons", ["year"])


def ingest_circuits():
    df = read_csv("circuits.csv")
    if df.empty:
        return
    df.columns = ["circuit_id", "circuit_ref", "name", "location", "country",
                   "lat", "lng", "alt", "url"]
    df["circuit_id"] = clean_column(df["circuit_id"], "int")
    df["lat"] = clean_column(df["lat"], "float")
    df["lng"] = clean_column(df["lng"], "float")
    df["alt"] = clean_column(df["alt"], "int")
    upsert_dataframe(df, "circuits", ["circuit_id"])


def ingest_drivers():
    df = read_csv("drivers.csv")
    if df.empty:
        return
    df.columns = ["driver_id", "driver_ref", "number", "code", "forename",
                   "surname", "dob", "nationality", "url"]
    df["driver_id"] = clean_column(df["driver_id"], "int")
    df["number"] = clean_column(df["number"], "int")
    df["code"] = clean_column(df["code"])
    df["dob"] = clean_column(df["dob"], "date")
    upsert_dataframe(df, "drivers", ["driver_id"])


def ingest_constructors():
    df = read_csv("constructors.csv")
    if df.empty:
        return
    df.columns = ["constructor_id", "constructor_ref", "name",
                   "nationality", "url"]
    df["constructor_id"] = clean_column(df["constructor_id"], "int")
    upsert_dataframe(df, "constructors", ["constructor_id"])


def ingest_status():
    df = read_csv("status.csv")
    if df.empty:
        return
    df.columns = ["status_id", "status"]
    df["status_id"] = clean_column(df["status_id"], "int")
    upsert_dataframe(df, "status", ["status_id"])


def ingest_races():
    df = read_csv("races.csv")
    if df.empty:
        return
    df.columns = ["race_id", "year", "round", "circuit_id", "name", "date",
                   "time", "url", "fp1_date", "fp1_time", "fp2_date", "fp2_time",
                   "fp3_date", "fp3_time", "quali_date", "quali_time",
                   "sprint_date", "sprint_time"]
    df["race_id"] = clean_column(df["race_id"], "int")
    df["year"] = clean_column(df["year"], "int")
    df["round"] = clean_column(df["round"], "int")
    df["circuit_id"] = clean_column(df["circuit_id"], "int")
    df["date"] = clean_column(df["date"], "date")
    for col in ["time", "fp1_time", "fp2_time", "fp3_time",
                "quali_time", "sprint_time"]:
        df[col] = clean_column(df[col], "time")
    for col in ["fp1_date", "fp2_date", "fp3_date", "quali_date", "sprint_date"]:
        df[col] = clean_column(df[col], "date")
    upsert_dataframe(df, "races", ["race_id"])


def ingest_results():
    df = read_csv("results.csv")
    if df.empty:
        return
    df.columns = ["result_id", "race_id", "driver_id", "constructor_id",
                   "number", "grid", "position", "position_text",
                   "position_order", "points", "laps", "time",
                   "milliseconds", "fastest_lap", "rank",
                   "fastest_lap_time", "fastest_lap_speed", "status_id"]
    int_cols = ["result_id", "race_id", "driver_id", "constructor_id",
                "number", "grid", "position", "position_order", "laps",
                "milliseconds", "fastest_lap", "rank", "status_id"]
    for col in int_cols:
        df[col] = clean_column(df[col], "int")
    df["points"] = clean_column(df["points"], "float")
    upsert_dataframe(df, "results", ["result_id"])


def ingest_qualifying():
    df = read_csv("qualifying.csv")
    if df.empty:
        return
    df.columns = ["qualify_id", "race_id", "driver_id", "constructor_id",
                   "number", "position", "q1", "q2", "q3"]
    for col in ["qualify_id", "race_id", "driver_id", "constructor_id",
                "number", "position"]:
        df[col] = clean_column(df[col], "int")
    upsert_dataframe(df, "qualifying", ["qualify_id"])


def ingest_sprint_results():
    df = read_csv("sprint_results.csv")
    if df.empty:
        return
    df.columns = ["sprint_result_id", "race_id", "driver_id", "constructor_id",
                   "number", "grid", "position", "position_text",
                   "position_order", "points", "laps", "time",
                   "milliseconds", "fastest_lap",
                   "fastest_lap_time", "status_id", "rank"]
    df["fastest_lap_speed"] = None
    int_cols = ["sprint_result_id", "race_id", "driver_id", "constructor_id",
                "number", "grid", "position", "position_order", "laps",
                "milliseconds", "fastest_lap", "rank", "status_id"]
    for col in int_cols:
        df[col] = clean_column(df[col], "int")
    df["points"] = clean_column(df["points"], "float")
    upsert_dataframe(df, "sprint_results", ["sprint_result_id"])


def ingest_lap_times():
    df = read_csv("lap_times.csv")
    if df.empty:
        return
    df.columns = ["race_id", "driver_id", "lap", "position", "time",
                   "milliseconds"]
    df = df.dropna(subset=["race_id", "driver_id", "lap"])
    for col in ["race_id", "driver_id", "lap", "position"]:
        df[col] = clean_column(df[col], "int")
    df["milliseconds"] = clean_column(df["milliseconds"], "int")
    upsert_dataframe(df, "lap_times", ["race_id", "driver_id", "lap"])


def ingest_pit_stops():
    df = read_csv("pit_stops.csv")
    if df.empty:
        return
    df.columns = ["race_id", "driver_id", "stop", "lap", "time",
                   "duration", "milliseconds"]
    for col in ["race_id", "driver_id", "stop", "lap"]:
        df[col] = clean_column(df[col], "int")
    df["milliseconds"] = clean_column(df["milliseconds"], "int")
    upsert_dataframe(df, "pit_stops", ["race_id", "driver_id", "stop"])


def ingest_driver_standings():
    df = read_csv("driver_standings.csv")
    if df.empty:
        return
    df.columns = ["driver_standing_id", "race_id", "driver_id", "points",
                   "position", "position_text", "wins"]
    for col in ["driver_standing_id", "race_id", "driver_id", "position", "wins"]:
        df[col] = clean_column(df[col], "int")
    df["points"] = clean_column(df["points"], "float")
    upsert_dataframe(df, "driver_standings", ["driver_standing_id"])


def ingest_constructor_standings():
    df = read_csv("constructor_standings.csv")
    if df.empty:
        return
    df.columns = ["constructor_standing_id", "race_id", "constructor_id",
                   "points", "position", "position_text", "wins"]
    for col in ["constructor_standing_id", "race_id", "constructor_id",
                "position", "wins"]:
        df[col] = clean_column(df[col], "int")
    df["points"] = clean_column(df["points"], "float")
    upsert_dataframe(df, "constructor_standings", ["constructor_standing_id"])


def ingest_constructor_results():
    df = read_csv("constructor_results.csv")
    if df.empty:
        return
    df.columns = ["constructor_results_id", "race_id", "constructor_id",
                   "points", "status"]
    for col in ["constructor_results_id", "race_id", "constructor_id"]:
        df[col] = clean_column(df[col], "int")
    df["points"] = clean_column(df["points"], "float")
    upsert_dataframe(df, "constructor_results", ["constructor_results_id"])


def main():
    logger.info("=" * 60)
    logger.info("F1 Race Analytics - Data Ingestion Pipeline")
    logger.info("=" * 60)

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful.")
    except Exception as e:
        logger.error(f"Cannot connect to database: {e}")
        sys.exit(1)

    logger.info("--- Phase 1: Independent/Lookup Tables ---")
    ingest_seasons()
    ingest_circuits()
    ingest_drivers()
    ingest_constructors()
    ingest_status()

    logger.info("--- Phase 2: Races ---")
    ingest_races()

    logger.info("--- Phase 3: Fact Tables ---")
    ingest_results()
    ingest_qualifying()
    ingest_sprint_results()
    ingest_lap_times()
    ingest_pit_stops()
    ingest_driver_standings()
    ingest_constructor_standings()
    ingest_constructor_results()

    logger.info("=" * 60)
    logger.info("Data ingestion complete. All tables loaded successfully.")
    logger.info("=" * 60)

    engine.dispose()
    logger.info("Database connections closed.")


if __name__ == "__main__":
    main()
