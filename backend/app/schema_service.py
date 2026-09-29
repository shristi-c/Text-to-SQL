from sqlalchemy import inspect

from backend.app.database import engine


def get_database_schema():
    inspector = inspect(engine)

    schemas = ["it", "retail", "airline"]

    database_schema = {}

    for schema_name in schemas:
        tables = inspector.get_table_names(schema=schema_name)

        database_schema[schema_name] = {}

        for table_name in tables:
            columns = inspector.get_columns(
                table_name,
                schema=schema_name,
            )

            database_schema[schema_name][table_name] = [
                {
                    "name": column["name"],
                    "type": str(column["type"]),
                    "nullable": column["nullable"],
                }
                for column in columns
            ]

    return database_schema