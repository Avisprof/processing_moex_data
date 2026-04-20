import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_DSN = os.getenv("POSTGRES_DSN", "postgresql://airflow:airflow@postgres:5432/airflow")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "moex_quotes")
MOEX_BASE_URL = os.getenv("MOEX_BASE_URL", "https://iss.moex.com/iss")
DEFAULT_TICKERS = [ticker.strip().upper() for ticker in os.getenv("DEFAULT_TICKERS", "SBER, LKOH, FIVE").split(",") if ticker.strip()]
SLEEP_INTERVAL_SECONDS = int(os.getenv("SLEEP_INTERVAL_SECONDS", "30"))
