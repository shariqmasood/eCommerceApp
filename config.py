# ====================
# config.py
# ====================
import os
from urllib.parse import uses_netloc
# Allow parsing of Postgres-style URLs if used
uses_netloc.append("postgres")

class Config:
    # Flask secret key for sessions
    SECRET_KEY                    = os.getenv("SECRET_KEY")
    # Database URI: Postgres or fallback to local SQLite
    SQLALCHEMY_DATABASE_URI       = os.getenv("DATABASE_URL") or "sqlite:///store.db"
    SQLALCHEMY_TRACK_MODIFICATIONS= False
    # 2Checkout merchant code for hosted checkout
    TCO_SELLER_ID                 = os.getenv("TCO_SELLER_ID")
    # Demo mode flag: "1" = test orders with demo=Y, "0" = live
    TCO_TEST_MODE                 = os.getenv("TCO_TEST_MODE", "1")