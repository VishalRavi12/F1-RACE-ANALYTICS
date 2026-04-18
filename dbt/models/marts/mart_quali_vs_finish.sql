with base as (
    select
        f.season_year,
        f.race_id,
        f.driver_id,
        f.constructor_id,
        q.qualifying_position,
        f.position_order as finish_position,
        f.points,
        q.qualifying_position - f.position_order as qualify_to_finish_delta
    from {{ ref('fact_race_results') }} as f
    left join {{ ref('stg_qualifying') }} as q
        on
            f.race_id = q.race_id
            and f.driver_id = q.driver_id
    where q.qualifying_position is not null
),

ranked as (
    select
        *,
        row_number() over (
            partition by season_year
            order by qualify_to_finish_delta desc, points desc
        ) as season_overperformance_rank
    from base
)

select *
from ranked
