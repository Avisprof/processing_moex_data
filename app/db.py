import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from .config import POSTGRES_DSN, DEFAULT_TICKERS


def get_connection():
    return psycopg2.connect(POSTGRES_DSN)


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tracked_tickers (
                    secid TEXT PRIMARY KEY,
                    shortname TEXT,
                    boardid TEXT NOT NULL DEFAULT 'TQBR',
                    active BOOLEAN NOT NULL DEFAULT TRUE,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_stock_prices (
                    secid TEXT NOT NULL,
                    boardid TEXT NOT NULL DEFAULT 'TQBR',
                    trade_date DATE NOT NULL,
                    open NUMERIC,
                    high NUMERIC,
                    low NUMERIC,
                    close NUMERIC,
                    volume BIGINT,
                    value NUMERIC,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                    PRIMARY KEY (secid, boardid, trade_date)
                )
                """
            )
            for secid in DEFAULT_TICKERS:
                cur.execute(
                    """
                    INSERT INTO tracked_tickers (secid, shortname, boardid, active)
                    VALUES (%s, %s, 'TQBR', TRUE)
                    ON CONFLICT (secid) DO UPDATE SET active = TRUE, shortname = COALESCE(tracked_tickers.shortname, EXCLUDED.shortname)
                    """,
                    (secid, secid),
                )
        conn.commit()


def get_tracked_tickers(include_inactive=False):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if include_inactive:
                cur.execute("SELECT secid, shortname, boardid, active FROM tracked_tickers ORDER BY secid")
            else:
                cur.execute("SELECT secid, shortname, boardid, active FROM tracked_tickers WHERE active = TRUE ORDER BY secid")
            return cur.fetchall()


def add_ticker(secid, shortname=None, boardid="TQBR"):
    if shortname is None:
        shortname = secid
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tracked_tickers (secid, shortname, boardid, active)
                VALUES (%s, %s, %s, TRUE)
                ON CONFLICT (secid) DO UPDATE SET shortname = EXCLUDED.shortname, boardid = EXCLUDED.boardid, active = TRUE
                """,
                (secid, shortname, boardid),
            )
        conn.commit()


def remove_ticker(secid):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE tracked_tickers SET active = FALSE, updated_at = now() WHERE secid = %s",
                (secid,),
            )
        conn.commit()


def get_price_history(secid, start_date=None, end_date=None):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = "SELECT trade_date, open, high, low, close, volume, value FROM daily_stock_prices WHERE secid = %s"
            params = [secid]
            if start_date is not None:
                query += " AND trade_date >= %s"
                params.append(start_date)
            if end_date is not None:
                query += " AND trade_date <= %s"
                params.append(end_date)
            query += " ORDER BY trade_date"
            cur.execute(query, params)
            rows = cur.fetchall()
    if not rows:
        return pd.DataFrame(columns=["trade_date", "open", "high", "low", "close", "volume", "value"])
    df = pd.DataFrame(rows)
    df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.date
    return df


def upsert_daily_price(stock_record):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO daily_stock_prices (secid, boardid, trade_date, open, high, low, close, volume, value)
                VALUES (%(secid)s, %(boardid)s, %(trade_date)s, %(open)s, %(high)s, %(low)s, %(close)s, %(volume)s, %(value)s)
                ON CONFLICT (secid, boardid, trade_date) DO UPDATE SET
                    open = COALESCE(daily_stock_prices.open, EXCLUDED.open),
                    high = GREATEST(COALESCE(daily_stock_prices.high, EXCLUDED.high), COALESCE(EXCLUDED.high, daily_stock_prices.high)),
                    low = LEAST(COALESCE(daily_stock_prices.low, EXCLUDED.low), COALESCE(EXCLUDED.low, daily_stock_prices.low)),
                    close = EXCLUDED.close,
                    volume = COALESCE(daily_stock_prices.volume, 0) + COALESCE(EXCLUDED.volume, 0),
                    value = EXCLUDED.value,
                    updated_at = now()
                """,
                stock_record,
            )
        conn.commit()


def get_ticker(secid):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT secid, shortname, boardid, active FROM tracked_tickers WHERE secid = %s", (secid,))
            return cur.fetchone()
