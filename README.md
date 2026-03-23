# F1-RACE-ANALYTICS

Formula 1 Race Analytics - Database Design & Data Ingestion Pipeline

**Course:** EAS 550 - Data Mining Query Language

**Team:** Karisha Ananya Neelakandan, Swaminathan Sankaran, Vishal Ravi Muthaiah

## ER Diagram

![ER Diagram](er_diagram.jpeg)

The schema consists of 14 tables in Third Normal Form (3NF):

- **Independent tables:** `seasons`, `circuits`, `drivers`, `constructors`, `status`
- **Dependent table:** `races` (references `seasons` and `circuits`)
- **Fact tables:** `results`, `qualifying`, `sprint_results`, `lap_times`, `pit_stops`, `driver_standings`, `constructor_standings`, `constructor_results`

## Database Schema (`schema.sql`)

Creates all 14 tables in dependency order with appropriate constraints:

- **Data types:** `INTEGER`, `SERIAL`, `VARCHAR`, `DECIMAL`, `DATE`, `TIME`, `BIGINT`
- **Constraints:** `PRIMARY KEY`, `FOREIGN KEY`, `NOT NULL`, `UNIQUE`, `CHECK`
- **Idempotent:** Drops all tables before recreating (`DROP TABLE IF EXISTS ... CASCADE`)
- **Indexes:** Performance indexes on frequently queried columns (`race_id`, `driver_id`, `constructor_id`, etc.)

## Data Ingestion Pipeline (`ingest_data.py`)

The ingestion script loads the [Ergast F1 dataset](https://www.kaggle.com/datasets/jtrotman/formula-1-race-data) (14 CSV files) into a Neon PostgreSQL database.

### How It Works

1. **Configuration** - Reads the `DATABASE_URL` environment variable and sets up a SQLAlchemy engine with connection pooling (`pool_size=3`, `pool_recycle=300s`) optimized for Neon's free tier.

2. **Data Cleaning (`clean_column`)** - Replaces Ergast's `\N` null markers with Python `None` and casts columns to appropriate types (`int`, `float`, `date`, `time`).

3. **Batch Upsert (`upsert_dataframe`)** - Uses `psycopg2.extras.execute_values` to insert rows in batches of 5000 for high performance. Each insert uses `ON CONFLICT DO NOTHING` to make the script fully idempotent (safe to re-run without duplicating data).

4. **Dependency-Ordered Loading** - Tables are loaded in three phases to satisfy foreign key constraints:
   - **Phase 1:** Independent/lookup tables (`seasons`, `circuits`, `drivers`, `constructors`, `status`)
   - **Phase 2:** `races` (depends on `seasons` and `circuits`)
   - **Phase 3:** Fact tables (`results`, `qualifying`, `sprint_results`, `lap_times`, `pit_stops`, `driver_standings`, `constructor_standings`, `constructor_results`)

5. **Connection Cleanup** - Disposes the engine after ingestion so Neon compute can auto-pause.

### Usage

```bash
# Set connection string
export DATABASE_URL="postgresql://user:pass@host/dbname?sslmode=require"

# Install dependencies
pip install -r requirements.txt

# Run schema (creates tables)
# Use Neon SQL Editor or: psql "$DATABASE_URL" -f schema.sql

# Run ingestion
python ingest_data.py
```

## Security & RBAC (`security.sql`)

Implements Role-Based Access Control with two roles:

- **`analyst_role`** - Read-only (`SELECT`) access on all tables. Intended for data analysts who need to query data but should not modify it.
- **`app_user_role`** - Read/write (`SELECT`, `INSERT`, `UPDATE`) access on all tables and sequences. Intended for application-level access (e.g., Streamlit/FastAPI).

Both roles use `NOLOGIN` and are designed to be granted to actual database users. `ALTER DEFAULT PRIVILEGES` ensures future tables automatically inherit the same permissions.

## Project Structure

```
Directory
├── data/                  # CSV files (not tracked in git)
├── schema.sql             # Database schema (3NF)
├── ingest_data.py         # Data ingestion pipeline
├── security.sql           # RBAC roles (bonus)
├── er_diagram.jpeg        # Entity-Relationship diagram
├── requirements.txt       # Python dependencies
├── .gitignore
└── README.md
```
