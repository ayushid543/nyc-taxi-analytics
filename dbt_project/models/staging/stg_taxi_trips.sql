with source as (
    select * from read_parquet('C:/Users/ayude/nyc_taxi_analytics/data/raw/yellow_tripdata_2024-01.parquet')
),

cleaned as (
    select
        VendorID                                    as vendor_id,
        tpep_pickup_datetime                        as pickup_datetime,
        tpep_dropoff_datetime                       as dropoff_datetime,
        passenger_count,
        trip_distance,
        PULocationID                                as pickup_location_id,
        DOLocationID                                as dropoff_location_id,
        fare_amount,
        tip_amount,
        total_amount,
        payment_type,
        date_trunc('hour', tpep_pickup_datetime)    as pickup_hour,
        dayofweek(tpep_pickup_datetime)             as day_of_week,
        hour(tpep_pickup_datetime)                  as hour_of_day,
        datediff('minute', tpep_pickup_datetime,
                 tpep_dropoff_datetime)             as trip_duration_minutes
    from source
    where
        fare_amount > 0
        and trip_distance > 0
        and passenger_count > 0
        and tpep_pickup_datetime >= '2024-01-01'
        and tpep_pickup_datetime < '2024-02-01'
)

select * from cleaned