from datetime import datetime
from app.moex_client import get_history, validate_ticker
from app.db import upsert_daily_price, add_ticker


def load_historical_data(secid: str, from_date: str, till_date: str):
    metadata = validate_ticker(secid)
    add_ticker(metadata["secid"], metadata.get("shortname"), metadata.get("boardid", "TQBR"))
    rows = get_history(metadata["secid"], from_date, till_date)
    if not rows:
        raise ValueError(f"No historical data found for {metadata['secid']} from {from_date} to {till_date}.")
    for row in rows:
        upsert_daily_price(row)
    return len(rows)
