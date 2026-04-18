with ranked as (
    select
        qualify_id,
        race_id,
        driver_id,
        constructor_id,
        number as driver_number,
        position as qualifying_position,
        q1,
        q2,
        q3,
        row_number() over (
            partition by race_id, driver_id
            order by position asc nulls last, qualify_id asc
        ) as row_priority
    from {{ source('f1_oltp', 'qualifying') }}
)

select
    qualify_id,
    race_id,
    driver_id,
    constructor_id,
    driver_number,
    qualifying_position,
    q1,
    q2,
    q3
from ranked
where row_priority = 1
