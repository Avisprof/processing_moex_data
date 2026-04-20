from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from app.kafka_aggregator import consume_and_aggregate

with DAG(
    dag_id="moex_ingest",
    schedule_interval="*/15 * * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args={
        "owner": "airflow",
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
    },
    max_active_runs=1,
    tags=["moex", "kafka", "postgres"],
) as dag:

    ingest_quotes = PythonOperator(
        task_id="consume_and_aggregate_kafka_quotes",
        python_callable=consume_and_aggregate,
    )

    ingest_quotes
