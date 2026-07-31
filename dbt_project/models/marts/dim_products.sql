with products as (

    select * from {{ ref('stg_products') }}

),

category_translation as (

    select * from {{ ref('stg_category_translation') }}

),

joined as (

    select
        products.product_id,
        products.product_category_name,
        category_translation.product_category_name_english,
        products.product_weight_g,
        products.product_length_cm,
        products.product_height_cm,
        products.product_width_cm

    from products
    left join category_translation
        on products.product_category_name = category_translation.product_category_name

)

select * from joined