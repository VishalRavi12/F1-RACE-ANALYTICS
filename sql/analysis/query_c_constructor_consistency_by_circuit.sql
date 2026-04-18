with constructor_circuit_results as (
    select
        r.year as season_year,
        r.race_id,
        r.circuit_id,
        ci.name as circuit_name,
        res.constructor_id,
        c.name as constructor_name,
        avg(res.position_order::numeric) as avg_finish_position,
        sum(res.points) as total_points,
        sum(case when res.position_order = 1 then 1 else 0 end) as wins,
        stddev_samp(res.position_order::numeric) as finish_position_stddev
    from results as res
    inner join races as r
        on res.race_id = r.race_id
    inner join circuits as ci
        on r.circuit_id = ci.circuit_id
    inner join constructors as c
        on res.constructor_id = c.constructor_id
    where res.position_order is not null
    group by
        r.year,
        r.race_id,
        r.circuit_id,
        ci.name,
        res.constructor_id,
        c.name
),

ranked as (
    select
        season_year,
        race_id,
        circuit_id,
        circuit_name,
        constructor_id,
        constructor_name,
        avg_finish_position,
        total_points,
        wins,
        finish_position_stddev,
        rank() over (
            partition by season_year, circuit_id
            order by avg_finish_position asc, total_points desc
        ) as constructor_rank_at_circuit
    from constructor_circuit_results
)

select
    season_year,
    circuit_id,
    circuit_name,
    constructor_id,
    constructor_name,
    avg_finish_position,
    total_points,
    wins,
    finish_position_stddev,
    constructor_rank_at_circuit
from ranked
where constructor_rank_at_circuit <= 5
order by season_year desc, circuit_name asc, constructor_rank_at_circuit asc;
