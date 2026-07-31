with order_items as (

    select * from {{ ref('stg_order_items') }}

),

aggregated as (

    select
        order_id,
        count(*) as total_items,
        sum(price) as total_items_price,
        sum(freight_value) as total_freight_value

    from order_items
    group by order_id

)

select * from aggregated