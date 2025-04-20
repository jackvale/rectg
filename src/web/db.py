import os
from sqlalchemy import create_engine
from flask import g
from dotenv import load_dotenv
from logger import log

load_dotenv(verbose=True)

DB_USER = os.getenv("DB_USER", None)
DB_PASSWORD = os.getenv("DB_PASSWORD", None)
DB_HOST = os.getenv("DB_HOST", None)
DB_PORT = os.getenv("DB_PORT", None)
DB_NAME = os.getenv("DB_NAME", None)


def get_db():
    if "db" not in g:
        log.info("Connecting to database")
        engine = create_engine(
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4",
            pool_pre_ping=True,
        )

        con = engine.connect()

        g.db = con
        return g.db


def close_db(e=None):
    log.info("close_db requested")
    db = g.pop("db", None)
    if db is not None:
        log.info("Closing db connection")
        db.close()
    else:
        log.info("db connection already closed. No action taken.")
