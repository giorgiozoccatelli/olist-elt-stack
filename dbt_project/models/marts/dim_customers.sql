with customers as (

    select * from {{ ref('stg_customers') }}

),

deduplicated as (

    select distinct on (customer_unique_id)
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state

    from customers
    order by customer_unique_id

)

select * from deduplicated