with orders as (

    select * from {{ ref('stg_orders') }}

),

customers as (

    select * from {{ ref('stg_customers') }}

),

items_summary as (

    select * from {{ ref('int_order_items_summary') }}

),

payments_summary as (

    select * from {{ ref('int_order_payments_summary') }}

),

reviews_summary as (

    select * from {{ ref('int_order_reviews_summary') }}

),

final as (

    select
        orders.order_id,
        orders.customer_id,
        customers.customer_unique_id,
        orders.order_status,
        orders.order_purchased_at,
        orders.order_approved_at,
        orders.order_delivered_customer_at,
        orders.order_estimated_delivery_at,

        items_summary.total_items,
        items_summary.total_items_price,
        items_summary.total_freight_value,

        payments_summary.total_payments,
        payments_summary.total_payment_value,

        reviews_summary.total_reviews,
        reviews_summary.avg_review_score,

        extract(day from (orders.order_delivered_customer_at - orders.order_purchased_at))
            as delivery_days

    from orders
    left join customers on orders.customer_id = customers.customer_id
    left join items_summary on orders.order_id = items_summary.order_id
    left join payments_summary on orders.order_id = payments_summary.order_id
    left join reviews_summary on orders.order_id = reviews_summary.order_id

)

select * from final