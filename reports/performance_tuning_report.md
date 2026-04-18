# Phase 2 Performance Tuning Report

## Query Under Test
- Query: `sql/analysis/query_b_pitstop_strategy_impact.sql`
- Baseline plan script: `sql/performance/query_b_baseline_explain.sql`
- Post-index plan script: `sql/performance/query_b_post_index_explain.sql`

## Index Strategy Implemented
Applied in `sql/performance/create_performance_indexes.sql`:
- `qualifying(race_id, driver_id, position)`
- `pit_stops(race_id, driver_id, milliseconds)`
- `results(race_id, driver_id, position_order)`

## Execution Steps
1. Run baseline explain:
   - `psql "$DATABASE_URL" -f sql/performance/query_b_baseline_explain.sql`
2. Create indexes:
   - `psql "$DATABASE_URL" -f sql/performance/create_performance_indexes.sql`
3. Run post-index explain:
   - `psql "$DATABASE_URL" -f sql/performance/query_b_post_index_explain.sql`

## Baseline Observations
- Planning Time: `1.437 ms`
- Execution Time: `84.163 ms`
- Top-level estimated cost: `2280.05`
- In join path from `qualifying` to `results`, planner used `idx_results_race` with extra row filtering:
  - `Index Cond: (race_id = q.race_id)`
  - `Filter: (driver_id = q.driver_id)`

## Post-Index Observations
- Planning Time: `1.698 ms`
- Execution Time: `46.564 ms`
- Top-level estimated cost: `1793.98`
- Planner switched to composite index `idx_results_race_driver_position_order` in the join path:
  - `Index Cond: ((race_id = q.race_id) AND (driver_id = q.driver_id))`
- This removed the additional filter step on `driver_id` for that index scan path.

## Before vs After Summary Table
| Metric | Baseline | Post-Index | Improvement |
|---|---:|---:|---:|
| Execution Time (ms) | 84.163 | 46.564 | 44.67% faster (`-37.599 ms`) |
| Planning Time (ms) | 1.437 | 1.698 | 18.16% slower (`+0.261 ms`) |
| Top-Level Estimated Cost | 2280.05 | 1793.98 | 21.32% lower (`-486.07`) |

## Expected Outcome
- Fewer expensive sequential scans on `qualifying`, `pit_stops`, and `results` join/filter paths.
- Lower end-to-end execution time for the pit-stop impact query.
- Outcome achieved in this run: query execution time improved by ~44.7% after index creation.
