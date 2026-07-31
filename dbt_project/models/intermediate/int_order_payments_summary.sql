with order_payments as (

    select * from {{ ref('stg_order_payments') }}

),

aggregated as (

    select
        order_id,
        count(*) as total_payments,
        sum(payment_value) as total_payment_value

    from order_payments
    group by order_id

)

select * from aggregated