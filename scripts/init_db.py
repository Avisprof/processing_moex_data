from app.db import init_db


if __name__ == "__main__":
    init_db()
    print("Database schema is ready and default tickers are configured.")
