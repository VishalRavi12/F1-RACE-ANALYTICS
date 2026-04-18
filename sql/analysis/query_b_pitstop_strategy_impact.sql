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
        r.name as race_name,
        res.driver_id,
        d.forename,
        d.surname,
        res.constructor_id,
        c.name as constructor_name,
        q.position as qualifying_position,
        res.grid,
        res.position_order as finish_position,
        res.points,
        ps.avg_pit_stop_ms,
        ps.total_pit_stop_ms,
        coalesce(ps.pit_stop_count, 0) as pit_stop_count,
        q.position - res.position_order as adjusted_finish_gain
    from results as res
    inner join races as r
        on res.race_id = r.race_id
    inner join drivers as d
        on res.driver_id = d.driver_id
    inner join constructors as c
        on res.constructor_id = c.constructor_id
    left join qualifying as q
        on
            res.race_id = q.race_id
            and res.driver_id = q.driver_id
    left join pit_strategy as ps
        on
            res.race_id = ps.race_id
            and res.driver_id = ps.driver_id
    where
        res.position_order is not null
        and q.position is not null
),

strategy_bands as (
    select
        season_year,
        race_id,
        race_name,
        driver_id,
        forename,
        surname,
        constructor_id,
        constructor_name,
        qualifying_position,
        grid,
        finish_position,
        points,
        avg_pit_stop_ms,
        total_pit_stop_ms,
        pit_stop_count,
        adjusted_finish_gain,
        ntile(4) over (
            partition by season_year
            order by coalesce(total_pit_stop_ms, 999999999)
        ) as pit_time_quartile,
        rank() over (
            partition by season_year
            order by adjusted_finish_gain desc, points desc
        ) as finish_gain_rank
    from race_performance
)

select
    season_year,
    race_id,
    race_name,
    driver_id,
    forename,
    surname,
    constructor_id,
    constructor_name,
    qualifying_position,
    grid,
    finish_position,
    adjusted_finish_gain,
    points,
    pit_stop_count,
    avg_pit_stop_ms,
    total_pit_stop_ms,
    pit_time_quartile,
    finish_gain_rank
from strategy_bands
order by season_year desc, finish_gain_rank asc, adjusted_finish_gain desc;
