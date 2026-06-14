with trips as (
    select * from {{ ref('stg_taxi_trips') }}
)

select
    pickup_hour,
    hour_of_day,
    day_of_week,
    count(*)                                            as total_trips,
    avg(trip_distance)                                  as avg_distance_miles,
    avg(trip_duration_minutes)                          as avg_duration_minutes,
    avg(fare_amount)                                    as avg_fare,
    avg(tip_amount)                                     as avg_tip,
    sum(total_amount)                                   as total_revenue,
    avg(tip_amount / nullif(fare_amount, 0)) * 100      as tip_pct
from trips
group by 1, 2, 3
order by 1