# F1 Race Analytics

A cloud-native data engineering pipeline over seven decades of Formula 1 racing data. Built for **EAS 550 — Data Mining Query Language** as a multi-phase group project covering relational modeling, dimensional modeling with dbt, automated data quality, CI/CD, and query performance tuning.

## Team

- Karisha Ananya Neelakandan
- Swaminathan Sankaran
- Vishal Ravi Muthaiah

## Dataset

- **Source:** [Ergast F1 dataset on Kaggle](https://www.kaggle.com/datasets/jtrotman/formula-1-race-data)
- **Coverage:** 1950 – present; 14 related CSV files (seasons, circuits, drivers, constructors, races, results, qualifying, sprint results, lap times, pit stops, standings, and status codes).
- **Why:** Rich relational structure across races, drivers, constructors, and circuits makes it a natural fit for 3NF modeling and a downstream star schema.

## Architecture

```
 Ergast CSVs ──▶ ingest_data.py ──▶ Neon PostgreSQL (3NF OLTP, 14 tables)
                                          │
                                          ▼
                                    dbt (staging → dims + facts → marts)
                                          │
                                          ▼
                               Analytical SQL + performance tuning
                                          │
                                          ▼
                             GitHub Actions (SQLFluff lint + dbt build/test)
```

## Tech Stack

| Layer | Tool |
| --- | --- |
| Storage | Neon (serverless PostgreSQL) |
| Ingestion | Python, Pandas, SQLAlchemy, psycopg2 |
| Transformation & Tests | dbt Core (postgres), `dbt_utils` |
| Linting | SQLFluff (with dbt templater) |
| CI/CD | GitHub Actions |
| Performance | `EXPLAIN (ANALYZE, BUFFERS)`, composite B-tree indexes |

## Validation Snapshot (Phase 2)

| Check | Result |
| --- | --- |
| `dbt test` | PASS = 41, ERROR = 0 |
| `dbt docs generate` | Catalog generated |
| `sqlfluff lint dbt/models` | Passed |
| `sqlfluff lint sql/analysis` | Passed |
| Query B tuning | 84.163 ms → 46.564 ms (**44.67% faster**) |

## Repository Layout

```
.
├── .github/workflows/ci.yml         # SQLFluff lint + dbt build/test on PR
├── dbt/
│   ├── dbt_project.yml
│   ├── packages.yml
│   ├── profiles.yml
│   └── models/
│       ├── sources.yml              # OLTP source declarations + source tests
│       ├── model_tests.yml          # PK/FK/business-rule tests
│       ├── staging/                 # stg_* views (type casts, renames)
│       ├── dimensions/              # dim_driver/constructor/circuit/race/status
│       ├── facts/                   # fact_race_results
│       └── marts/                   # analytics-ready aggregate tables
├── docs/star_schema_diagram.md      # Mermaid ERD for the star schema
├── sql/
│   ├── analysis/                    # 3 CTE + window-function queries
│   └── performance/                 # Baseline/post-index EXPLAIN + index DDL
├── reports/
│   ├── performance_tuning_report.md
│   ├── baseline_explain.txt
│   └── post_index_explain.txt
├── schema.sql                       # Phase 1 OLTP DDL (3NF)
├── ingest_data.py                   # Idempotent ELT pipeline
├── security.sql                     # RBAC (analyst + app_user roles)
├── er_diagram.jpeg                  # Phase 1 ERD
├── DMQL_PHASE_1_REPORT.pdf          # Phase 1 justification report
├── requirements.txt                 # Runtime deps
├── requirements-dev.txt             # Lint/dbt deps
└── README.md
```

---

## Phase 1 — Relational Modeling & Ingestion

### Artifacts
- 3NF schema: [`schema.sql`](schema.sql)
- Idempotent ELT pipeline: [`ingest_data.py`](ingest_data.py)
- RBAC (bonus): [`security.sql`](security.sql)
- ER diagram: [`er_diagram.jpeg`](er_diagram.jpeg)
- Phase 1 report: [`DMQL_PHASE_1_REPORT.pdf`](DMQL_PHASE_1_REPORT.pdf)

### Schema design
Fourteen tables in Third Normal Form:
- **Lookup / dimension-like**: `seasons`, `circuits`, `drivers`, `constructors`, `status`
- **Race-level**: `races` (FKs to `seasons`, `circuits`; carries practice / qualifying / sprint schedule fields)
- **Fact-like**: `results`, `qualifying`, `sprint_results`, `lap_times`, `pit_stops`, `driver_standings`, `constructor_standings`, `constructor_results`

Integrity is enforced with `PRIMARY KEY`, `FOREIGN KEY`, `NOT NULL`, `UNIQUE`, and `CHECK` constraints. Appropriate types are used for each column (`DECIMAL` for points, `DATE`/`TIME` for schedules, `BIGINT` for milliseconds).

### Ingestion pipeline
`ingest_data.py` uses Pandas + SQLAlchemy + psycopg2 `execute_values` for batched upserts:
- Normalizes Ergast's `\N` null markers and enforces target dtypes.
- Inserts tables in dependency order to satisfy foreign keys.
- Uses `ON CONFLICT DO NOTHING` so re-runs are fully idempotent.
- Configures `QueuePool` with `pool_size=3`, `pool_recycle=300`, `pool_pre_ping=True` to stay inside Neon's free-tier compute budget and dispose cleanly at end of run.

### RBAC (bonus)
`security.sql` creates two roles with least-privilege defaults:
- `analyst_role` — read-only access.
- `app_user_role` — `SELECT`, `INSERT`, `UPDATE` plus sequence usage for downstream apps.

`ALTER DEFAULT PRIVILEGES` ensures future tables inherit the same grants.

---

## Phase 2 — Dimensional Modeling, Tests & CI

### dbt project
- Config: [`dbt/dbt_project.yml`](dbt/dbt_project.yml)
- Env-driven profile: [`dbt/profiles.yml`](dbt/profiles.yml)
- Packages: [`dbt/packages.yml`](dbt/packages.yml) (`dbt_utils`)

### Star schema
Diagram: [`docs/star_schema_diagram.md`](docs/star_schema_diagram.md)

Layers:
- **Staging (views):** one `stg_*` model per OLTP source — type casts, renames, and null normalization.
- **Dimensions (tables):** `dim_driver`, `dim_constructor`, `dim_circuit`, `dim_race`, `dim_status`.
- **Fact (table):** `fact_race_results` — grain is one row per `(race_id, driver_id)`. Deterministic `row_number()` ordering removes ambiguous duplicates before downstream marts consume the fact.
- **Marts (tables):**
  - `mart_quali_vs_finish` — qualifying-to-finish delta per driver per race.
  - `mart_pitstop_impact` — pit-stop counts, times, and season-level efficiency ranking.
  - `mart_driver_constructor_performance` — aggregated season performance by `(year, driver, constructor)`.

### Data quality tests
Defined in [`dbt/models/sources.yml`](dbt/models/sources.yml) and [`dbt/models/model_tests.yml`](dbt/models/model_tests.yml):
- **Primary-key integrity:** `unique` + `not_null` on every PK column.
- **Referential integrity:** `relationships` tests from every fact FK to its dimension.
- **Grain checks:** `dbt_utils.unique_combination_of_columns` on fact and mart natural keys.
- **Business rules** via `dbt_utils.expression_is_true`:
  - `position_order is null or position_order > 0`
  - `grid is null or grid >= 0`
  - `points >= 0`

### Advanced analytical SQL
Each query uses CTEs and window functions and runs directly against the 3NF OLTP layer:

| Query | Question answered | File |
| --- | --- | --- |
| A | Which drivers most overperform their qualifying position each season? | [`sql/analysis/query_a_quali_to_finish_overperformers.sql`](sql/analysis/query_a_quali_to_finish_overperformers.sql) |
| B | How does pit-stop strategy correlate with finishing gain, controlling for qualifying position? | [`sql/analysis/query_b_pitstop_strategy_impact.sql`](sql/analysis/query_b_pitstop_strategy_impact.sql) |
| C | Which constructors are most consistent at each circuit across seasons? | [`sql/analysis/query_c_constructor_consistency_by_circuit.sql`](sql/analysis/query_c_constructor_consistency_by_circuit.sql) |

### Performance tuning
Query B was profiled with `EXPLAIN (ANALYZE, BUFFERS)` before and after a targeted indexing pass.

Composite B-tree indexes added (also mirrored in [`schema.sql`](schema.sql)):
- `qualifying(race_id, driver_id, position)`
- `pit_stops(race_id, driver_id, milliseconds)`
- `results(race_id, driver_id, position_order)`

| Metric | Baseline | Post-index | Improvement |
| --- | ---: | ---: | ---: |
| Execution time | 84.163 ms | 46.564 ms | **−44.67%** |
| Top-level estimated cost | 2280.05 | 1793.98 | −21.32% |

Full report: [`reports/performance_tuning_report.md`](reports/performance_tuning_report.md). Raw plans: [`reports/baseline_explain.txt`](reports/baseline_explain.txt), [`reports/post_index_explain.txt`](reports/post_index_explain.txt).

### Continuous integration
Workflow: [`.github/workflows/ci.yml`](.github/workflows/ci.yml). Triggered on every pull request to `main`.

| Job | What it does |
| --- | --- |
| `sqlfluff_lint` | Spins up a Postgres service container so the dbt templater can resolve `{{ ref() }}` and `{{ source() }}`, then lints `dbt/models` (dbt templater) and `sql/analysis` (jinja templater). |
| `dbt_test` | Installs `dbt-postgres`, runs `dbt deps`, then `dbt build --select +fact_race_results+` against Neon using repository secrets. |

SQLFluff rules live in [`.sqlfluff`](.sqlfluff) (Postgres dialect, dbt templater, 120-char line limit, lower-case keywords).

---

## Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Configure environment variables

A template is provided in [`.env.example`](.env.example); `ingest_data.py` auto-loads `.env` via `python-dotenv`:

```bash
cp .env.example .env
# edit .env with your Neon credentials
```

To run `dbt` or `psql` in the same shell, export the values:

```bash
set -a
source .env
set +a
```

### 3. Build and load the OLTP layer

```bash
psql "$DATABASE_URL" -f schema.sql
python ingest_data.py
psql "$DATABASE_URL" -f security.sql
```

`ingest_data.py` is idempotent — re-running it is safe and will not duplicate rows.

### 4. Build the analytics layer

```bash
dbt deps   --project-dir dbt --profiles-dir dbt
dbt debug  --project-dir dbt --profiles-dir dbt
dbt build  --project-dir dbt --profiles-dir dbt
dbt docs generate --project-dir dbt --profiles-dir dbt
dbt docs serve    --project-dir dbt --profiles-dir dbt
```

### 5. Lint locally

```bash
sqlfluff lint dbt/models   --config .sqlfluff
sqlfluff lint sql/analysis --dialect postgres --templater jinja
```

### 6. Reproduce the Query B performance study

```bash
psql "$DATABASE_URL" -P pager=off -f sql/performance/query_b_baseline_explain.sql
psql "$DATABASE_URL"             -f sql/performance/create_performance_indexes.sql
psql "$DATABASE_URL" -P pager=off -f sql/performance/query_b_post_index_explain.sql
```

## GitHub Secrets required for CI

The `dbt_test` job expects the following repository secrets pointing at the Neon instance used for CI:

- `DBT_HOST`
- `DBT_PORT`
- `DBT_USER`
- `DBT_PASSWORD`
- `DBT_DATABASE`
- `DBT_SCHEMA`
- `DBT_THREADS`

No credentials are ever committed to the repository.
