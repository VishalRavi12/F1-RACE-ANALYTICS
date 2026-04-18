with pit_agg as (
    select
        race_id,
        driver_id,
        count(*) as pit_stop_count,
        avg(stop_milliseconds) as avg_pit_stop_ms,
        sum(stop_milliseconds) as total_pit_stop_ms
    from {{ ref('stg_pit_stops') }}
    group by race_id, driver_id
),

joined as (
    select
        f.season_year,
        f.race_id,
        f.driver_id,
        f.constructor_id,
        q.qualifying_position,
        f.grid,
        f.position_order as finish_position,
        f.finish_position_delta,
        p.avg_pit_stop_ms,
        p.total_pit_stop_ms,
        f.points,
        coalesce(p.pit_stop_count, 0) as pit_stop_count
    from {{ ref('fact_race_results') }} as f
    left join {{ ref('stg_qualifying') }} as q
        on
            f.race_id = q.race_id
            and f.driver_id = q.driver_id
    left join pit_agg as p
        on
            f.race_id = p.race_id
            and f.driver_id = p.driver_id
),

scored as (
    select
        *,
        case
            when qualifying_position is null then null
            else qualifying_position - finish_position
        end as adjusted_finish_gain,
        rank() over (
            partition by season_year
            order by coalesce(total_pit_stop_ms, 0) asc, points desc
        ) as pit_efficiency_rank_in_season
    from joined
)

select *
from scored
