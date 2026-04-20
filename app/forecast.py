import pandas as pd
from prophet import Prophet


def forecast_price(history_df, days: int = 7):
    df = history_df[["trade_date", "close"]].copy()
    df = df.dropna()
    if len(df) < 10:
        raise ValueError("At least 10 historical daily values are required for forecasting.")
    df["ds"] = pd.to_datetime(df["trade_date"])
    df["y"] = df["close"].astype(float)
    model = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=False)
    model.fit(df[["ds", "y"]])
    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)
    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]
