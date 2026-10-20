import os

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

POSTGRES_URL = (
    f"postgresql+psycopg2://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
    f"@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}"
)
MARTS = "analytics_marts"


@st.cache_data(ttl=600)
def run_query(sql: str) -> pd.DataFrame:
    return pd.read_sql(sql, create_engine(POSTGRES_URL))


st.set_page_config(page_title="Olist e-commerce", layout="wide")
st.title("Olist e-commerce dashboard")
st.caption("Data from the dbt marts (analytics_marts), refreshed by the Airflow pipeline.")

# KPIs
kpi = run_query(f"""
    select
        count(*) as orders,
        sum(total_items_price) as revenue,
        avg(avg_review_score) as avg_review_score,
        avg(delivery_days) as avg_delivery_days
    from {MARTS}.fct_orders
""").iloc[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Orders", f"{int(kpi['orders']):,}")
col2.metric("Revenue (R$)", f"{kpi['revenue']:,.0f}")
col3.metric("Avg review score", f"{kpi['avg_review_score']:.2f}")
col4.metric("Avg delivery days", f"{kpi['avg_delivery_days']:.1f}")

left, right = st.columns(2)

# Revenue per day
with left:
    st.subheader("Daily revenue (R$)")
    daily = run_query(f"""
        select order_purchased_at::date as day, sum(total_items_price) as revenue
        from {MARTS}.fct_orders
        group by 1 order by 1
    """)
    st.line_chart(daily, x="day", y="revenue")

# Orders by status
with right:
    st.subheader("Orders by status")
    status = run_query(f"""
        select order_status, count(*) as orders
        from {MARTS}.fct_orders
        group by 1 order by 2 desc
    """)
    st.bar_chart(status, x="order_status", y="orders")

left, right = st.columns(2)

# Top categories
with left:
    st.subheader("Top 10 categories by revenue (R$)")
    categories = run_query(f"""
        select coalesce(p.product_category_name_english, 'untranslated') as category,
               sum(i.price) as revenue
        from {MARTS}.fct_order_items i
        left join {MARTS}.dim_products p on i.product_id = p.product_id
        group by 1 order by 2 desc limit 10
    """)
    st.bar_chart(categories, x="category", y="revenue", horizontal=True)

# Late deliveries
with right:
    st.subheader("Delivery performance")
    late = run_query(f"""
        select
            count(*) as delivered,
            count(*) filter (where order_delivered_customer_at > order_estimated_delivery_at) as late
        from {MARTS}.fct_orders
        where order_delivered_customer_at is not null
    """).iloc[0]
    st.metric("Delivered orders", f"{int(late['delivered']):,}")
    st.metric("Delivered late", f"{late['late'] / late['delivered']:.1%}")
