import os
from pathlib import Path

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago

from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig,RenderConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping
from cosmos.constants import TestBehavior

DEFAULT_DBT_ROOT_PATH = Path(__file__).parent / "dbt"
DBT_ROOT_PATH = Path(os.getenv("DBT_ROOT_PATH", DEFAULT_DBT_ROOT_PATH))


project_config = ProjectConfig(
    dbt_project_path=(DBT_ROOT_PATH / "localiza_dw").as_posix()
)

profile_config = ProfileConfig(
    profile_name="localiza_dw",
    target_name="prod",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id="localiza_dw",
        profile_args={"schema": "dm_credit_operations"}
    )
)


with DAG(
    dag_id="dag_dbt-model_credit_fraud",
    schedule=None,
    start_date=days_ago(1),
    catchup=False,
    is_paused_upon_creation=False,
    tags=['datamart', 'credit_fraud'],
) as dag:

    pre_dbt_workflow = EmptyOperator(task_id="pre_dbt_workflow")

    model_credit_fraud = DbtTaskGroup(
        group_id="model_credit_fraud",
        project_config=project_config,
        render_config=RenderConfig(
            test_behavior=TestBehavior.AFTER_ALL,
            select=["path:models/staging/credit_fraud",
                    "path:models/marts/credit_fraud",
                    "path:snapshots/credit_fraud"]
        ),
        execution_config=ExecutionConfig(
            dbt_executable_path="/usr/local/airflow/dbt_venv/bin/dbt"
        ),
        operator_args={"install_deps": True},
        profile_config=profile_config,
        default_args={"retries": 0},
        dag=dag,
    )


    pre_dbt_workflow >> model_credit_fraud
