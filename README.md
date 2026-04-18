# F1-RACE-ANALYTICS

Formula 1 Race Analytics for **EAS 550 (DMQL)**.

This repository now includes:
- **Phase 1**: 3NF OLTP schema, ingestion pipeline, and RBAC.
- **Phase 2**: dbt star-schema analytics layer, data quality tests, SQL linting CI, advanced analytical SQL, and performance tuning artifacts.

### Validation Snapshot (Phase 2)
- `dbt test` completed successfully (`PASS=41, ERROR=0`).
- `dbt docs generate` successfully produced catalog artifacts.
- `sqlfluff lint dbt/models --config .sqlfluff` passed.
- `sqlfluff lint sql/analysis --dialect postgres --templater jinja` passed.

## Team
- Karisha Ananya Neelakandan
- Swaminathan Sankaran
- Vishal Ravi Muthaiah

## Dataset
- Ergast F1 dataset (Kaggle): https://www.kaggle.com/datasets/jtrotman/formula-1-race-data

## Phase 1 (Completed)

### Core artifacts
- 3NF schema: [`schema.sql`](schema.sql)
- Ingestion pipeline: [`ingest_data.py`](ingest_data.py)
- RBAC (bonus): [`security.sql`](security.sql)
- ER diagram: [`er_diagram.jpeg`](er_diagram.jpeg)
- 3NF report: [`DMQL_PHASE_1_REPORT.pdf`](DMQL_PHASE_1_REPORT.pdf)

### Ingestion behavior
- Loads 14 CSV files into Neon PostgreSQL.
- Handles null markers (`\\N`) and type cleanup.
- Inserts in dependency order to satisfy foreign keys.
- Uses conflict-safe inserts (`ON CONFLICT DO NOTHING`) for idempotency.

## Phase 2 (Implemented)

### dbt analytics project
- Root: [`dbt/`](dbt/)
- dbt config: [`dbt/dbt_project.yml`](dbt/dbt_project.yml)
- profile (env-driven): [`dbt/profiles.yml`](dbt/profiles.yml)
- packages: [`dbt/packages.yml`](dbt/packages.yml)

### Star schema
- Diagram: [`docs/star_schema_diagram.md`](docs/star_schema_diagram.md)

Models:
- **Staging (views)**: `stg_*` models in [`dbt/models/staging`](dbt/models/staging)
- **Dimensions (tables)**: `dim_driver`, `dim_constructor`, `dim_circuit`, `dim_race`, `dim_status`
- **Fact (table)**: `fact_race_results` (grain: one driver per race)
- **Data harmonization in modeling**: de-duplicates ambiguous source rows in `qualifying` and `results` using deterministic `row_number()` ranking before downstream marts.
- **Marts (tables)**:
  - `mart_quali_vs_finish`
  - `mart_pitstop_impact`
  - `mart_driver_constructor_performance`

### Data quality tests
- Source/model tests and business-rule tests are defined in:
  - [`dbt/models/sources.yml`](dbt/models/sources.yml)
  - [`dbt/models/model_tests.yml`](dbt/models/model_tests.yml)

Includes:
- PK uniqueness and not-null checks
- Fact-to-dimension referential integrity checks
- Business rules via `dbt_utils.expression_is_true`:
  - `position_order is null or position_order > 0`
  - `grid is null or grid >= 0`
  - `points >= 0`

### SQL linting and CI/CD
- SQLFluff config: [`.sqlfluff`](.sqlfluff)
- GitHub Actions workflow: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

Workflow behavior on `pull_request` to `main`:
1. `sqlfluff_lint` job
   - Installs `dbt-postgres`, `sqlfluff`, `sqlfluff-templater-dbt`
   - Runs lint on dbt models and advanced SQL queries
2. `dbt_test` job
   - Uses Neon credentials from GitHub Secrets
   - Runs `dbt deps` and `dbt build --select +fact_race_results+`

### Advanced analytical SQL (CTE + window functions)
- Query A (qualifying vs finish over/under-performance):
  - [`sql/analysis/query_a_quali_to_finish_overperformers.sql`](sql/analysis/query_a_quali_to_finish_overperformers.sql)
- Query B (pit-stop strategy impact controlling for qualifying):
  - [`sql/analysis/query_b_pitstop_strategy_impact.sql`](sql/analysis/query_b_pitstop_strategy_impact.sql)
- Query C (constructor consistency by circuit and season):
  - [`sql/analysis/query_c_constructor_consistency_by_circuit.sql`](sql/analysis/query_c_constructor_consistency_by_circuit.sql)

### Performance tuning artifacts
- Baseline `EXPLAIN ANALYZE`: [`sql/performance/query_b_baseline_explain.sql`](sql/performance/query_b_baseline_explain.sql)
- Strategic indexes: [`sql/performance/create_performance_indexes.sql`](sql/performance/create_performance_indexes.sql)
- Post-index `EXPLAIN ANALYZE`: [`sql/performance/query_b_post_index_explain.sql`](sql/performance/query_b_post_index_explain.sql)
- Final report: [`reports/performance_tuning_report.md`](reports/performance_tuning_report.md)

Measured outcome from Query B tuning:
- Execution time improved from `84.163 ms` to `46.564 ms` (`44.67%` faster).

`schema.sql` also includes the three composite indexes used for Query B optimization.

## Setup

## 1) Python dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## 2) Environment variables

For ingestion (either export directly or use a local `.env` file):

```bash
export DATABASE_URL="postgresql://user:pass@host/dbname?sslmode=require"
export CSV_DIR="./data"
```

`.env` option:

```bash
cp .env.example .env
# edit .env with your real values
```

`ingest_data.py` auto-loads `.env` via `python-dotenv`.
For `dbt` and `psql`, load `.env` into your shell:

```bash
set -a
source .env
set +a
```

For dbt (local + CI parity):

```bash
export DBT_HOST="<neon-host>"
export DBT_PORT="5432"
export DBT_USER="<db-user>"
export DBT_PASSWORD="<db-password>"
export DBT_DATABASE="<db-name>"
export DBT_SCHEMA="analytics"
export DBT_THREADS="4"
```

## 3) Run Phase 1 pipeline

```bash
psql "$DATABASE_URL" -f schema.sql
python ingest_data.py
psql "$DATABASE_URL" -f security.sql
```

If your Phase 1 database is already populated, you can skip re-running `ingest_data.py`.

## 4) Run Phase 2 dbt pipeline

```bash
dbt deps --project-dir dbt --profiles-dir dbt
dbt debug --project-dir dbt --profiles-dir dbt
dbt build --project-dir dbt --profiles-dir dbt
dbt test --project-dir dbt --profiles-dir dbt
dbt docs generate --project-dir dbt --profiles-dir dbt
```

## 5) Run SQL lint checks locally

```bash
sqlfluff lint dbt/models --config .sqlfluff
sqlfluff lint sql/analysis --dialect postgres --templater jinja
```

## 6) Run performance tuning sequence

```bash
psql "$DATABASE_URL" -P pager=off -f sql/performance/query_b_baseline_explain.sql
psql "$DATABASE_URL" -f sql/performance/create_performance_indexes.sql
psql "$DATABASE_URL" -P pager=off -f sql/performance/query_b_post_index_explain.sql
```

Then fill measured timings in [`reports/performance_tuning_report.md`](reports/performance_tuning_report.md).

## GitHub Secrets required for CI
- `DBT_HOST`
- `DBT_PORT`
- `DBT_USER`
- `DBT_PASSWORD`
- `DBT_DATABASE`
- `DBT_SCHEMA`
- `DBT_THREADS`

## Repository structure

```text
.
├── .github/workflows/ci.yml
├── dbt/
│   ├── dbt_project.yml
│   ├── packages.yml
│   ├── profiles.yml
│   └── models/
│       ├── sources.yml
│       ├── model_tests.yml
│       ├── staging/
│       ├── dimensions/
│       ├── facts/
│       └── marts/
├── docs/star_schema_diagram.md
├── sql/
│   ├── analysis/
│   └── performance/
├── reports/performance_tuning_report.md
├── schema.sql
├── ingest_data.py
├── security.sql
├── requirements.txt
├── requirements-dev.txt
└── README.md
```
