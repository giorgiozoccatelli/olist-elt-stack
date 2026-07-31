with order_items as (

    select * from {{ ref('stg_order_items') }}

),

orders as (

    select * from {{ ref('stg_orders') }}

),

customers as (

    select * from {{ ref('stg_customers') }}

),

final as (

    select
        order_items.order_id,
        order_items.order_item_id,
        order_items.product_id,
        order_items.seller_id,
        customers.customer_unique_id,
        orders.order_purchased_at,
        order_items.price,
        order_items.freight_value

    from order_items
    left join orders on order_items.order_id = orders.order_id
    left join customers on orders.customer_id = customers.customer_id

)

select * from final