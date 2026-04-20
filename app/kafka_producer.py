import json
import time
from kafka import KafkaProducer
from app.config import KAFKA_BROKER, KAFKA_TOPIC, SLEEP_INTERVAL_SECONDS
from app.db import init_db, get_tracked_tickers
from app.moex_client import get_market_snapshot


def create_producer():
    return KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        retries=5,
    )


def run_producer():
    init_db()
    producer = create_producer()
    while True:
        tickers = get_tracked_tickers()
        if not tickers:
            print("No active tickers configured. Waiting to retry.")
            time.sleep(SLEEP_INTERVAL_SECONDS)
            continue

        for item in tickers:
            try:
                snapshot = get_market_snapshot(item["secid"], item.get("boardid", "TQBR"))
                if snapshot is None:
                    print(f"No snapshot available for {item['secid']}")
                    continue
                producer.send(KAFKA_TOPIC, snapshot)
                print(f"Produced snapshot for {item['secid']}")
            except Exception as exc:
                print(f"Failed to produce snapshot for {item['secid']}: {exc}")

        producer.flush()
        time.sleep(SLEEP_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_producer()
