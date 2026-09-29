from fastapi import FastAPI
from sqlalchemy import text

from backend.app.database import engine
from backend.app.schema_service import get_database_schema
from backend.app.sql_validator import validate_sql
from backend.app.sql_service import execute_sql
from backend.app.query_service import process_question



app = FastAPI(
    title="Text-to-SQL API",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Text-to-SQL Backend Running"
    }


@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.scalar()

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@app.get("/schema")
def database_schema():
    return get_database_schema()

@app.post("/validate-sql")
def validate_sql_query(sql: str):
    return validate_sql(sql)

@app.post("/execute-sql")
def execute_sql_query(sql: str):
    validation = validate_sql(sql)

    if not validation["valid"]:
        return {
            "success": False,
            "error": validation["reason"],
        }

    try:
        result = execute_sql(sql)

        return {
            "success": True,
            "data": result,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }

@app.post("/execute-sql")
def execute_sql_query(sql: str):
    validation = validate_sql(sql)

    if not validation["valid"]:
        return {
            "success": False,
            "error": validation["reason"],
        }

    try:
        result = execute_sql(sql)

        return {
            "success": True,
            "data": result,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@app.post("/query")
def query_database(question: str):
    return process_question(question)

@app.post("/query")
def query_database(question: str):
    return process_question(question)