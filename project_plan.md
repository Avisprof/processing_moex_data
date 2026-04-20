# Project Plan: MOEX Stock Data Pipeline and Dashboard

## 1. Project Overview

Build an end-to-end data engineering project for Moscow Exchange (MOEX) stock prices using a streaming ingestion pipeline, workflow orchestration, analytics database, and an interactive dashboard with forecasting.

Key goals:
- Stream stock quotes from the MOEX API through Kafka
- Orchestrate scheduled data processing with Apache Airflow
- Store aggregated time-series data in PostgreSQL
- Build a Streamlit frontend for ticker selection, historical charts, and 7-day forecasts
- Support manual data loading for missing historical periods and ticker management

## 2. Requirements and Scope

Core functionality:
- Kafka producer connects to MOEX API and publishes quote data for selected tickers
- Kafka consumer or Airflow DAG reads stream data and aggregates it into PostgreSQL
- Streamlit app allows users to:
  - select tracked tickers
  - add and remove tickers
  - load missing historical data on demand
  - display daily stock price charts
  - show a 7-day forecast using a simple ML model such as Prophet

Initial tracked tickers:
- Sberbank
- Lukoil
- X5 Retail Group

## 3. Architecture and Components

1. Kafka streaming layer
   - Producer service queries MOEX API for configured tickers
   - Publishes quote events to Kafka topics
   - Consumer or Airflow ingestion reads from Kafka

2. Airflow orchestration
   - DAG schedule: every 15 minutes for near-real-time updates
   - Tasks:
     - read data from Kafka topic
     - aggregate quotes into daily OHLC and volume summaries
     - write aggregated records into PostgreSQL
     - optionally backfill missing historical intervals

3. Data storage
   - PostgreSQL database with a stock price fact table
   - Partition by date or ticker if needed for query performance
   - Store metadata for tickers and ingestion status

4. Streamlit dashboard
   - Ticker management UI: add, remove, refresh symbols
   - Manual historical load button with date range input
   - Daily price chart for selected ticker
   - Forecast chart overlay from ML prediction

5. Forecasting model
   - Use Prophet or an equivalent time-series model
   - Train on historical daily prices
   - Predict next 7 days and plot predicted values with a distinct color

## 4. Technology Stack

- Python
- Docker Compose
- Kafka
- Apache Airflow
- PostgreSQL
- Streamlit
- Prophet (or alternative time-series library)
- MOEX API for market quotes

## 5. Detailed Work Plan

### Phase 1: Data Ingestion and Streaming
- Implement Kafka producer to fetch quotes from MOEX API
- Create topics for stock quote events
- Add configuration for tracked tickers and polling frequency
- Validate event format and schema

### Phase 2: Workflow Orchestration
- Build Airflow DAG for ingestion and aggregation
- Design DAG schedule: every 15 minutes
- Add tasks to consume Kafka events, aggregate daily data, and write to PostgreSQL
- Implement error handling and logging

### Phase 3: Database and Transformation
- Create PostgreSQL schema for stock price history
- Define fact table for daily OHLC and volume
- Optional: add partitioning by date for query efficiency
- Implement simple SQL transformations if needed

### Phase 4: Frontend and User Interaction
- Build Streamlit app with ticker selection and management
- Add manual import controls for historical data
- Display daily stock chart for selected ticker
- Add interactive UI for selecting date ranges and forecasting

### Phase 5: Forecasting and Model Integration
- Train a Prophet model on daily historical data
- Generate 7-day forecast for the selected ticker
- Plot actual values and forecast in the Streamlit chart
- Add explanatory text and model note

### Phase 6: Documentation and Reproducibility
- Add clear run instructions for Docker Compose and Airflow
- Document how to start Kafka, PostgreSQL, Airflow, and Streamlit
- Provide usage examples for manual data load and ticker management

## 6. Evaluation Alignment

- Problem description: clearly explain the real-world need for streaming MOEX quotes and forecasting
- Cloud / reproducibility: use Docker Compose for reproducible local/cloud deployment
- Data ingestion: implement Kafka streaming with producer and consumer, Airflow orchestration DAG
- Data warehouse: use PostgreSQL with meaningful schema and optional partitioning
- Transformations: include aggregation logic in Airflow and SQL
- Dashboard: build Streamlit interface with charts and forecast tile(s)
- Reproducibility: provide a documented project setup and launch sequence

## 7. Suggested Timeline

- Week 1: design data pipeline and implement Kafka producer + Airflow DAG
- Week 2: create PostgreSQL schema, complete ingestion, and verify data flow
- Week 3: build Streamlit dashboard and ticker management UI
- Week 4: integrate forecasting, finalize documentation, and polish deployment

## 8. Future Enhancements

- Add provenance metadata and ingestion audit logs
- Use a dedicated OLAP or cloud data warehouse for analytic queries
- Implement full backfill support for the Streamlit manual load feature
- Add multi-day forecasting and model selection options
- Create Grafana dashboards for system metrics and data quality
