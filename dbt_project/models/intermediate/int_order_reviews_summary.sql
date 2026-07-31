with order_reviews as (

    select * from {{ ref('stg_order_reviews') }}

),

aggregated as (

    select
        order_id,
        count(*) as total_reviews,
        avg(review_score) as avg_review_score

    from order_reviews
    group by order_id

)

select * from aggregated