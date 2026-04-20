# MOEX Stock Data Pipeline

This project implements a streaming stock quote pipeline for the Moscow Exchange (MOEX) with Kafka, Airflow, PostgreSQL, and Streamlit.

## Architecture

- `producer` service polls MOEX market data and publishes stock snapshots to Kafka.
- `airflow` DAG reads Kafka messages every 15 minutes and writes aggregated daily entries into PostgreSQL.
- `streamlit` app provides ticker management, manual historical data loading, daily charting, and a 7-day forecast.
- `grafana` is included in the compose stack for optional visualization.

## Services

- `postgres`: PostgreSQL database
- `zookeeper` / `kafka`: Kafka streaming layer
- `airflow-webserver` / `airflow-scheduler`: Airflow orchestration
- `producer`: Kafka producer for MOEX snapshots
- `streamlit`: frontend application
- `grafana`: optional metrics dashboard

## Getting Started

1. Copy environment variables:

```bash
cp .env.example .env
```

2. Start the stack:

```bash
docker compose up --build
```

3. Open the services:

- Streamlit: http://localhost:8501
- Airflow: http://localhost:8080 (login `admin` / `admin`)
- Grafana: http://localhost:3000 (login `admin` / `admin`)

## Streamlit Features

- Add and deactivate tracked tickers
- Load missing historical data for a ticker
- View daily price chart
- Display a 7-day forecast using Prophet

## Airflow DAG

The Airflow DAG `moex_ingest` runs every 15 minutes and consumes Kafka messages from topic `moex_quotes`.

## Notes

- Default tickers: `SBER`, `LKOH`, `FIVE`
- Historical data is loaded from the MOEX ISS API
- The system persists aggregated daily stock prices in PostgreSQL
