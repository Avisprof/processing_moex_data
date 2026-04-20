import requests
from datetime import date
from .config import MOEX_BASE_URL


def normalize_ticker(secid):
    return secid.strip().upper()


def fetch_security(secid):
    url = f"{MOEX_BASE_URL}/engines/stock/markets/shares/securities/{secid}.json"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    payload = response.json()
    securities = payload.get("securities", {})
    columns = securities.get("columns", [])
    data = securities.get("data", [])
    if not data:
        return None
    row = data[0]
    result = {col: row[idx] if idx < len(row) else None for idx, col in enumerate(columns)}
    return {
        "secid": result.get("SECID"),
        "shortname": result.get("SHORTNAME") or secid,
        "boardid": result.get("BOARDID") or "TQBR",
    }


def validate_ticker(secid):
    secid = normalize_ticker(secid)
    metadata = fetch_security(secid)
    if metadata is None:
        raise ValueError(f"Ticker {secid} not found on MOEX")
    return metadata


def get_market_snapshot(secid, boardid="TQBR"):
    secid = normalize_ticker(secid)
    url = f"{MOEX_BASE_URL}/engines/stock/markets/shares/securities/{secid}/marketdata.json"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    payload = response.json()
    marketdata = payload.get("marketdata", {})
    columns = marketdata.get("columns", [])
    data = marketdata.get("data", [])
    if not data:
        return None
    row = data[0]
    record = {col: row[idx] if idx < len(row) else None for idx, col in enumerate(columns)}
    trade_date = date.today().isoformat()
    return {
        "secid": secid,
        "boardid": boardid,
        "trade_date": trade_date,
        "open": record.get("OPEN"),
        "high": record.get("HIGH"),
        "low": record.get("LOW"),
        "close": record.get("LAST") or record.get("CLOSEPRICE"),
        "volume": record.get("VOLTODAY") or record.get("QTY") or 0,
        "value": record.get("VALTODAY") or record.get("VALUE") or 0,
        "timestamp": record.get("UPDATETIME") or record.get("SYSTIME"),
    }


def get_history(secid, from_date, till_date):
    secid = normalize_ticker(secid)
    params = {
        "from": from_date,
        "till": till_date,
    }
    url = f"{MOEX_BASE_URL}/history/engines/stock/markets/shares/securities/{secid}.json"
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    payload = response.json()
    history = payload.get("history", {})
    columns = history.get("columns", [])
    rows = history.get("data", [])
    if not rows:
        return []
    indexes = {name: idx for idx, name in enumerate(columns)}
    results = []
    for row in rows:
        trade_date = row[indexes["TRADEDATE"]]
        close_price = row[indexes["CLOSEPRICE"]] if "CLOSEPRICE" in indexes else None
        legal_close = row[indexes["LEGALCLOSEPRICE"]] if "LEGALCLOSEPRICE" in indexes else None
        results.append(
            {
                "secid": secid,
                "boardid": row[indexes["BOARDID"]] if "BOARDID" in indexes else "TQBR",
                "trade_date": trade_date,
                "open": row[indexes["OPEN"]] if "OPEN" in indexes else None,
                "high": row[indexes["HIGH"]] if "HIGH" in indexes else None,
                "low": row[indexes["LOW"]] if "LOW" in indexes else None,
                "close": close_price if close_price is not None else legal_close,
                "volume": row[indexes["NUMTRADES"]] if "NUMTRADES" in indexes else 0,
                "value": row[indexes["VALUE"]] if "VALUE" in indexes else 0,
            }
        )
    return results
