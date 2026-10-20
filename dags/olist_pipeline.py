from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
from cosmos import DbtTaskGroup, ExecutionConfig, ProfileConfig, ProjectConfig, RenderConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping

INGESTION_DIR = "/opt/airflow/ingestion"

# Cosmos builds the dbt profile from the Airflow connection "olist_postgres".
profile_config = ProfileConfig(
    profile_name="dbt_project",
    target_name="dev",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id="olist_postgres",
        profile_args={"schema": "analytics"},
    ),
)

with DAG(
    dag_id="olist_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["olist"],
) as dag:

    with TaskGroup(group_id="ingestion") as ingestion:
        prepare = BashOperator(
            task_id="prepare_batches",
            bash_command=f"python {INGESTION_DIR}/prepare_batches.py",
        )
        upload = BashOperator(
            task_id="upload_to_minio",
            bash_command=f"python {INGESTION_DIR}/upload_to_minio.py",
        )
        load = BashOperator(
            task_id="load_to_postgres",
            bash_command=f"python {INGESTION_DIR}/load_to_postgres.py",
        )
        prepare >> upload >> load

    # One Airflow task per dbt model; tests run after each model and stop downstream models on failure.
    transform = DbtTaskGroup(
        group_id="dbt",
        project_config=ProjectConfig("/opt/airflow/dbt_project"),
        profile_config=profile_config,
        execution_config=ExecutionConfig(dbt_executable_path="/home/airflow/dbt_venv/bin/dbt"),
        # Dataset events are not needed here and fail to save on Airflow 2.11.
        render_config=RenderConfig(emit_datasets=False),
    )

    notify = BashOperator(
        task_id="notify",
        bash_command='echo "Pipeline completed: ingestion and dbt models + tests passed."',
    )

    ingestion >> transform >> notify
