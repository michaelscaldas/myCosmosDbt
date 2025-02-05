from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 2, 3),
    'retries': 1
}


with DAG(
    dag_id='dag_ingestion_daily-credit_fraud',
    default_args=default_args,
    start_date=days_ago(1),
    schedule='0 4 * * *',
    catchup=False,
    is_paused_upon_creation=False,
    tags=['data_ingestion', 'raw_data'],
) as dag:

    # Cria a tabela no banco de dados
    create_table = PostgresOperator(
        task_id="create_table",
        postgres_conn_id="localiza_dw",
        sql="""
            CREATE SCHEMA IF NOT EXISTS dm_credit_operations_stage;
            DROP TABLE IF EXISTS dm_credit_operations_stage.raw_credit_fraud CASCADE;
            CREATE TABLE dm_credit_operations_stage.raw_credit_fraud (
               timestamp VARCHAR(50) NULL,
               sending_address VARCHAR(50) NULL,
               receiving_address VARCHAR(50) NULL,
               amount VARCHAR(50) NULL,
               transaction_type VARCHAR(50) NULL,
               location_region VARCHAR(50) NULL,
               ip_prefix VARCHAR(50) NULL,
               login_frequency VARCHAR(50) NULL,
               session_duration VARCHAR(50) NULL,
               purchase_pattern VARCHAR(50) NULL,
               age_group VARCHAR(50) NULL,
               risk_score VARCHAR(50) NULL,
               anomaly VARCHAR(50) NULL
          );
        """
    )

    # Comando COPY (assume que o arquivo está acessível ao servidor PostgreSQL)
    copy_csv_to_table = PostgresOperator(
        task_id="bulk_file_load",
        postgres_conn_id="localiza_dw",
        sql="""
            COPY dm_credit_operations_stage.raw_credit_fraud FROM '/data/raw_fraud_credit.csv' DELIMITER ',' CSV HEADER;
        """
    )


    # Trigger da DAG de processamento
    trigger_processing_dag = TriggerDagRunOperator(
        task_id="trigger_dag_dbt-model_credit_fraud",
        trigger_dag_id="dag_dbt-model_credit_fraud",  # Nome da DAG a ser triggerada
        execution_date="{{ ds }}",  # Passa a data de execução
        reset_dag_run=True,  # Reinicia a DAG se já tiver sido executada nesse contexto
        wait_for_completion=False  # Não aguarda a execução da outra DAG
    )

    create_table >> copy_csv_to_table >> trigger_processing_dag
