with trips as (
    select * from {{ ref('stg_taxi_trips') }}
),

payment_lookup as (
    select * from (values
        (1, 'Credit Card'),
        (2, 'Cash'),
        (3, 'No Charge'),
        (4, 'Dispute'),
        (5, 'Unknown')
    ) t(payment_type_id, payment_type_name)
)

select
    p.payment_type_name,
    count(*)                as total_trips,
    sum(t.total_amount)     as total_revenue,
    avg(t.tip_amount)       as avg_tip,
    avg(t.fare_amount)      as avg_fare
from trips t
left join payment_lookup p
    on t.payment_type = p.payment_type_id
group by 1
order by 2 desc