from sqlalchemy import inspect

from backend.app.database import engine


schemas = ["it", "retail", "airline"]

_cached_schema = None


def get_database_schema():
    global _cached_schema

    if _cached_schema is not None:
        return _cached_schema

    inspector = inspect(engine)

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

    _cached_schema = database_schema

    return _cached_schema


def get_domain_schema(domain: str):
    domain = domain.lower().strip()

    if domain not in schemas:
        raise ValueError(
            f"Invalid domain '{domain}'. "
            f"Allowed domains: {', '.join(schemas)}"
        )

    database_schema = get_database_schema()

    return {
        domain: database_schema[domain]
    }