import os
import json

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def save_query_history(
    question,
    domain,
    sql,
    answer,
    result,
    row_count,
    execution_time_ms,
    original_sql=None,
    original_error=None,
    corrected=False,
):
    with engine.begin() as connection:
        connection.execute(
            text("""
                INSERT INTO app.query_history (
                    question,
                    domain,
                    sql,
                    answer,
                    result,
                    row_count,
                    execution_time_ms,
                    original_sql,
                    original_error,
                    corrected
                )
                VALUES (
                    :question,
                    :domain,
                    :sql,
                    :answer,
                    CAST(:result AS JSONB),
                    :row_count,
                    :execution_time_ms,
                    :original_sql,
                    :original_error,
                    :corrected
                )
            """),
            {
                "question": question,
                "domain": domain,
                "sql": sql,
                "answer": answer,
                "result": json.dumps(result, default=str),
                "row_count": row_count,
                "execution_time_ms": execution_time_ms,
                "original_sql": original_sql,
                "original_error": original_error,
                "corrected": corrected,
            },
        )


def get_query_history(limit=50):
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                    id,
                    question,
                    domain,
                    sql,
                    answer,
                    result,
                    row_count,
                    execution_time_ms,
                    original_sql,
                    original_error,
                    corrected,
                    created_at
                FROM app.query_history
                ORDER BY created_at DESC
                LIMIT :limit
            """),
            {
                "limit": limit,
            },
        )

        rows = result.mappings().all()

    return [dict(row) for row in rows]