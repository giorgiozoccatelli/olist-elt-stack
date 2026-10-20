FROM apache/airflow:2.11.2-python3.12

# dbt lives in its own virtualenv so its dependencies cannot clash with Airflow's.
# Cosmos is pointed at /home/airflow/dbt_venv/bin/dbt.
RUN python -m venv /home/airflow/dbt_venv \
    && /home/airflow/dbt_venv/bin/pip install --no-cache-dir "dbt-core<2" "dbt-postgres<2"

# Airflow-side libraries. The constraints file pins versions known to work with Airflow 2.11.2.
COPY requirements-airflow.txt /tmp/requirements-airflow.txt
RUN pip install --no-cache-dir -r /tmp/requirements-airflow.txt \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.11.2/constraints-3.12.txt"
