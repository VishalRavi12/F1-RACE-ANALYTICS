explain analyze
with pit_strategy as (
    select
        race_id,
        driver_id,
        count(*) as pit_stop_count,
        avg(milliseconds) as avg_pit_stop_ms,
        sum(milliseconds) as total_pit_stop_ms
    from pit_stops
    group by race_id, driver_id
),
race_performance as (
    select
        r.year as season_year,
        r.race_id,
        res.driver_id,
        res.constructor_id,
        q.position as qualifying_position,
        res.position_order as finish_position,
        res.points,
        coalesce(ps.pit_stop_count, 0) as pit_stop_count,
        ps.avg_pit_stop_ms,
        ps.total_pit_stop_ms,
        q.position - res.position_order as adjusted_finish_gain
    from results as res
    inner join races as r
        on res.race_id = r.race_id
    left join qualifying as q
        on res.race_id = q.race_id
        and res.driver_id = q.driver_id
    left join pit_strategy as ps
        on res.race_id = ps.race_id
        and res.driver_id = ps.driver_id
    where res.position_order is not null
      and q.position is not null
)
select
    season_year,
    race_id,
    driver_id,
    constructor_id,
    qualifying_position,
    finish_position,
    adjusted_finish_gain,
    points,
    pit_stop_count,
    avg_pit_stop_ms,
    total_pit_stop_ms
from race_performance;
