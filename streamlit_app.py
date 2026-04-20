import altair as alt
import pandas as pd
import streamlit as st
from datetime import date, timedelta
from app.config import DEFAULT_TICKERS
from app.db import init_db, get_tracked_tickers, add_ticker, remove_ticker, get_price_history
from app.historical_loader import load_historical_data
from app.moex_client import validate_ticker
from app.forecast import forecast_price


def render_price_chart(history_df: pd.DataFrame):
    if history_df.empty:
        st.warning("No daily price data available. Use manual load to fetch historical data.")
        return

    history_df = history_df.copy()
    history_df["trade_date"] = pd.to_datetime(history_df["trade_date"])
    line_chart = alt.Chart(history_df).mark_line(point=True).encode(
        x="trade_date:T",
        y=alt.Y("close:Q", title="Close price"),
    ).properties(width=800, height=400)
    st.altair_chart(line_chart, use_container_width=True)


def render_forecast(history_df: pd.DataFrame):
    try:
        forecast_df = forecast_price(history_df, days=7)
    except Exception as exc:
        st.info(str(exc))
        return

    forecast_df = forecast_df.rename(columns={"ds": "trade_date"})
    forecast_df["trade_date"] = pd.to_datetime(forecast_df["trade_date"])
    forecast_df["type"] = forecast_df["trade_date"].apply(
        lambda ts: "Forecast" if ts > pd.to_datetime(history_df["trade_date"].max()) else "History"
    )
    actual_df = history_df[["trade_date", "close"]].copy()
    actual_df["trade_date"] = pd.to_datetime(actual_df["trade_date"])
    actual_df["type"] = "Actual"
    actual_df = actual_df.rename(columns={"close": "price"})

    forecast_plot = pd.concat(
        [
            actual_df,
            forecast_df[["trade_date", "yhat"]].rename(columns={"yhat": "price"}).assign(type="Forecast"),
        ],
        ignore_index=True,
    )

    chart = alt.Chart(forecast_plot).mark_line(point=True).encode(
        x="trade_date:T",
        y=alt.Y("price:Q", title="Price"),
        color="type:N",
    ).properties(width=800, height=420)
    st.altair_chart(chart, use_container_width=True)


def main():
    init_db()
    st.set_page_config(page_title="MOEX Stock Tracker", layout="wide")
    st.title("MOEX Stock Tracker")
    st.markdown(
        "Use the sidebar to manage tracked tickers, load historical data, and view daily price analytics with a 7-day forecast."
    )

    tickers = get_tracked_tickers(include_inactive=True)
    active_ticker_ids = [ticker["secid"] for ticker in tickers if ticker["active"]]
    all_ticker_ids = [ticker["secid"] for ticker in tickers]

    with st.sidebar:
        st.header("Ticker Management")
        add_symbol = st.text_input("Add new ticker", value="")
        add_button = st.button("Add ticker")
        if add_button and add_symbol:
            try:
                metadata = validate_ticker(add_symbol)
                add_ticker(metadata["secid"], metadata.get("shortname"), metadata.get("boardid", "TQBR"))
                st.success(f"Added {metadata['secid']}.")
                if metadata["secid"] not in all_ticker_ids:
                    all_ticker_ids.append(metadata["secid"])
                if metadata["secid"] not in active_ticker_ids:
                    active_ticker_ids.append(metadata["secid"])
            except Exception as exc:
                st.error(f"Failed to add ticker: {exc}")

        st.write("**Active tickers**")
        if active_ticker_ids:
            for ticker_id in active_ticker_ids:
                st.write(f"- {ticker_id}")
        else:
            st.warning("No active tickers. Add a ticker to start.")

        if all_ticker_ids:
            remove_symbol = st.selectbox("Remove ticker", options=all_ticker_ids)
            if st.button("Deactivate ticker"):
                remove_ticker(remove_symbol)
                st.success(f"Deactivated {remove_symbol}.")

    st.header("Historical loader")
    selected_ticker = st.selectbox(
        "Choose a tracked ticker", options=active_ticker_ids or DEFAULT_TICKERS
    )
    col1, col2 = st.columns(2)
    with col1:
        from_date = st.date_input("From date", value=date.today() - timedelta(days=90))
    with col2:
        till_date = st.date_input("Till date", value=date.today())

    if st.button("Load missing historical data"):
        try:
            loaded = load_historical_data(selected_ticker, from_date.isoformat(), till_date.isoformat())
            st.success(f"Loaded {loaded} historical rows for {selected_ticker}.")
        except Exception as exc:
            st.error(str(exc))

    st.header(f"Daily price chart for {selected_ticker}")
    history_df = get_price_history(selected_ticker)
    if history_df.empty:
        st.warning("No daily records found yet. Use the loader to add historical data.")
    else:
        latest = history_df.iloc[-1]
        st.metric("Latest close", f"{latest['close']}", delta=None)
        render_price_chart(history_df)
        st.subheader("7-day forecast")
        render_forecast(history_df)


if __name__ == "__main__":
    main()
