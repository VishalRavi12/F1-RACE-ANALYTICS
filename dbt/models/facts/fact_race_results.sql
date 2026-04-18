with ranked_results as (
    select
        r.*,
        row_number() over (
            partition by r.race_id, r.driver_id
            order by
                case when r.position_order is null then 1 else 0 end,
                r.position_order asc nulls last,
                r.points desc,
                r.result_id asc
        ) as row_priority
    from {{ ref('stg_results') }} as r
)

select
    rr.race_id,
    rr.driver_id,
    rr.constructor_id,
    rr.status_id,
    dr.season_year,
    rr.result_id,
    rr.driver_number,
    rr.grid,
    rr.position,
    rr.position_text,
    rr.position_order,
    rr.points,
    rr.laps,
    rr.result_time,
    rr.milliseconds,
    rr.fastest_lap,
    rr.fastest_lap_rank,
    rr.fastest_lap_time,
    rr.fastest_lap_speed,
    rr.grid - rr.position_order as finish_position_delta
from ranked_results as rr
inner join {{ ref('dim_race') }} as dr
    on rr.race_id = dr.race_id
where rr.row_priority = 1
