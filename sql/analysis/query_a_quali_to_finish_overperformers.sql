with race_outcomes as (
    select
        r.year as season_year,
        r.race_id,
        r.name as race_name,
        d.driver_id,
        d.forename,
        d.surname,
        q.position as qualifying_position,
        res.position_order as finish_position,
        res.points,
        q.position - res.position_order as overperformance_delta
    from results as res
    inner join races as r
        on res.race_id = r.race_id
    inner join drivers as d
        on res.driver_id = d.driver_id
    inner join qualifying as q
        on
            res.race_id = q.race_id
            and res.driver_id = q.driver_id
    where
        q.position is not null
        and res.position_order is not null
),

ranked as (
    select
        season_year,
        race_id,
        race_name,
        driver_id,
        forename,
        surname,
        qualifying_position,
        finish_position,
        points,
        overperformance_delta,
        dense_rank() over (
            partition by season_year
            order by overperformance_delta desc, points desc
        ) as season_rank
    from race_outcomes
)

select
    season_year,
    race_id,
    race_name,
    driver_id,
    forename,
    surname,
    qualifying_position,
    finish_position,
    overperformance_delta,
    points,
    season_rank
from ranked
where season_rank <= 10
order by season_year desc, season_rank asc, overperformance_delta desc;
