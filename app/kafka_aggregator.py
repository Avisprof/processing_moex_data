import json
from kafka import KafkaConsumer
from app.config import KAFKA_BROKER, KAFKA_TOPIC
from app.db import upsert_daily_price


def consume_and_aggregate(max_wait_seconds: int = 15, max_messages: int = 500):
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="moex-airflow-group",
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        consumer_timeout_ms=max_wait_seconds * 1000,
    )

    count = 0
    for message in consumer:
        payload = message.value
        try:
            upsert_daily_price(payload)
            count += 1
        except Exception as exc:
            print(f"Failed to upsert record for {payload.get('secid')}: {exc}")

    consumer.close()
    print(f"Consumed and upserted {count} Kafka messages.")
    return count
