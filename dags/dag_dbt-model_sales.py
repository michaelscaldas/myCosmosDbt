import os
from pathlib import Path

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago

from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig,RenderConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping
from cosmos.constants import TestBehavior
import json

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
        profile_args={"schema": "dm_sales"}
    )
)


with DAG(
    dag_id="dag_dbt-model_sales",
    schedule='0 4 * * *',
    start_date=days_ago(1),
    catchup=False,
    is_paused_upon_creation=False,
    params={"prod": "P003",
            "limite_quantidade": "500",
            "data_inicio": "1999-01-01",
            "data_fim": "2025-02-05"},
    tags=['datamart', 'sales'],
) as dag:

    pre_dbt_workflow = EmptyOperator(task_id="pre_dbt_workflow")

    # Construção dinâmica da string JSON dos vars
    vars_dict = {
        "PROD": "{{ params.prod }}",
        "LIMITE_QUANTIDADE": "{{ params.limite_quantidade }}",
        "DATA_INICIO": "{{ params.data_inicio }}",
        "DATA_FIM": "{{ params.data_fim }}"
    }

    model_sales = DbtTaskGroup(
        group_id="model_sales",
        project_config=project_config,
        render_config=RenderConfig(
            test_behavior=TestBehavior.AFTER_ALL,
            select=["path:seeds",
                    "path:models/marts/sales"]
        ),
        execution_config=ExecutionConfig(
            dbt_executable_path="/usr/local/airflow/dbt_venv/bin/dbt"
        ),
        operator_args={"install_deps": True,
                       "vars": json.dumps(vars_dict)},
        profile_config=profile_config,
        default_args={"retries": 0},
        dag=dag,
    )


    pre_dbt_workflow >> model_sales
