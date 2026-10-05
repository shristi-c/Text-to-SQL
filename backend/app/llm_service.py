
import os

from dotenv import load_dotenv
from groq import Groq

from backend.app.schema_service import get_domain_schema


load_dotenv("backend/.env")


api_key = os.getenv("GROQ_API_KEY")
model = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b",
)


if not api_key:
    raise RuntimeError("GROQ_API_KEY is not set")


client = Groq(api_key=api_key)


def format_schema(schema):
    lines = []

    for schema_name, tables in schema.items():
        lines.append(f"SCHEMA: {schema_name}")

        for table_name, table_data in tables.items():
            columns = table_data["columns"]

            column_names = ", ".join(
                column["name"] for column in columns
            )

            lines.append(
                f"TABLE: {schema_name}.{table_name} "
                f"({column_names})"
            )

            relationships = table_data.get(
                "relationships",
                [],
            )

            for relationship in relationships:
                lines.append(
                    f"RELATIONSHIP: "
                    f"{schema_name}.{table_name}."
                    f"{relationship['column']} -> "
                    f"{relationship['references_schema']}."
                    f"{relationship['references_table']}."
                    f"{relationship['references_column']}"
                )

    return "\n".join(lines)


def generate_sql(
    question: str,
    domain: str,
    conversation_context=None,
):
    schema = get_domain_schema(domain)

    schema_text = format_schema(schema)

    context_text = ""

    if conversation_context:
        previous_question = conversation_context.get(
            "question"
        )

        previous_sql = conversation_context.get(
            "sql"
        )

        previous_result = conversation_context.get(
            "result"
        )

        if previous_question:
            context_text += f"""
PREVIOUS USER QUESTION:
{previous_question}
"""

        if previous_sql:
            context_text += f"""
PREVIOUS SQL:
{previous_sql}
"""

        if previous_result:
            context_text += f"""
PREVIOUS QUERY RESULT:
{previous_result}
"""

    prompt = f"""
You are a Text-to-SQL system.

Convert the user's natural-language question into a PostgreSQL SQL query.

SELECTED DATABASE DOMAIN:
{domain}

DATABASE SCHEMA:
{schema_text}

{context_text}

FOLLOW-UP QUESTION HANDLING:
- If previous conversation context is provided, determine whether the current question refers to the previous question or result.
- Resolve references such as "their", "those", "that", "only those", "now show", "top 10", "what about 2025", and similar follow-up wording using the previous context.
- If the current question is independent, answer it normally using the database schema.
- The current user question always has priority over the previous context.
- Do not blindly reuse the previous SQL if the current question requires a different query.

RULES:
- Generate only SELECT queries.
- Do not generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, GRANT, REVOKE, EXECUTE, or CALL.
- Use only tables and columns that exist in the provided schema.
- Always use the correct schema-qualified table name.
- Use the provided relationship information when joins are required.
- Do not invent tables or columns.
- Do not use markdown code fences.
- Return only the SQL query.
- Do not include explanations.

CURRENT USER QUESTION:
{question}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
    )

    sql = response.choices[0].message.content.strip()

    return sql

