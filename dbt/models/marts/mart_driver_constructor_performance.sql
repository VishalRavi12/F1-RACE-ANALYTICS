with season_driver as (
    select
        f.season_year,
        f.driver_id,
        f.constructor_id,
        count(*) as races_participated,
        sum(f.points) as total_points,
        avg(f.position_order::numeric) as avg_finish_position,
        sum(case when f.position_order = 1 then 1 else 0 end) as wins,
        sum(case when f.position_order <= 3 then 1 else 0 end) as podiums
    from {{ ref('fact_race_results') }} as f
    group by f.season_year, f.driver_id, f.constructor_id
),

scored as (
    select
        sd.*,
        rank() over (
            partition by sd.season_year
            order by sd.total_points desc, sd.wins desc
        ) as driver_rank_in_season,
        rank() over (
            partition by sd.season_year, sd.constructor_id
            order by sd.total_points desc, sd.wins desc
        ) as constructor_internal_driver_rank
    from season_driver as sd
)

select
    s.season_year,
    s.driver_id,
    d.driver_full_name,
    s.constructor_id,
    c.constructor_name,
    s.races_participated,
    s.total_points,
    s.avg_finish_position,
    s.wins,
    s.podiums,
    s.driver_rank_in_season,
    s.constructor_internal_driver_rank
from scored as s
inner join {{ ref('dim_driver') }} as d
    on s.driver_id = d.driver_id
inner join {{ ref('dim_constructor') }} as c
    on s.constructor_id = c.constructor_id
