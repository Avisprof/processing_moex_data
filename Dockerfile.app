FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    libpq-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

RUN pip install uv

WORKDIR /app

RUN pip install streamlit==1.26.0 kafka-python==2.0.2 psycopg2-binary==2.9.10 pandas==2.2.2 prophet==1.2.2 requests==2.31.0 sqlalchemy==2.0.19 python-dotenv==1.0.0 altair==5.4.0

COPY . /app
