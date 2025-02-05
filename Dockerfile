FROM quay.io/astronomer/astro-runtime:11.3.0

# Instalação do dbt no ambiente virtual
RUN python -m venv /usr/local/airflow/dbt_venv && \
    . /usr/local/airflow/dbt_venv/bin/activate && \
    pip install dbt-core dbt-postgres && deactivate


# Copie as DAGs e dependências locais
COPY ./dags /usr/local/airflow/dags