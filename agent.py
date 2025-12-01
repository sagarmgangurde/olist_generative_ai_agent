import os
import textwrap
from dotenv import load_dotenv

from groq import Groq  # ✅ Direct Groq client

from .schema_reader import read_schema
from .tools import run_sql, df_to_markdown

load_dotenv()

# -----------------------------
# Groq Client
# -----------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set in your .env file")

client = Groq(api_key=GROQ_API_KEY)


# -----------------------------
# Helper: call Groq chat
# -----------------------------
def _chat(messages, temperature: float = 0.0) -> str:
    """Low-level helper to call Groq and return assistant content."""
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content or ""


# -----------------------------
# Helper: extract SQL from ```sql``` block
# -----------------------------
def _extract_sql(text: str) -> str:
    text = text.strip()
    if "```" not in text:
        return text  # assume it's just raw SQL

    # Try to pull out the first ```sql ... ``` block
    parts = text.split("```")
    for i in range(len(parts) - 1):
        block = parts[i + 1]
        if block.lower().startswith("sql"):
            # remove leading "sql" and any newline
            return block[3:].lstrip("\n\r")
    # fallback – return everything
    return text


# -----------------------------
# Main public function
# -----------------------------
def ask_agent(question: str) -> str:
    """
    Main entry point used by FastAPI & Streamlit.

    Steps:
    1. Get DB schema.
    2. Ask LLM to write ONLY SQL (no explanation).
    3. Run SQL on SQLite.
    4. Ask LLM to summarize the result.
    5. Return final markdown string.
    """
    try:
        # 1) Read schema once
        schema_json = read_schema()

        # 2) Ask LLM to write SQL
        system_sql = textwrap.dedent(
            """
            You are an expert SQL data analyst for the Olist Brazilian E-commerce dataset.

            You are given:
            - A user question.
            - The SQLite database schema (tables + columns).

            TASK:
            - Write ONE valid SQLite SELECT query that answers the question.
            - Use only the tables and columns that exist in the schema.
            - Do NOT explain anything.
            - Return ONLY the SQL inside a ```sql ... ``` code block.
            """
        )

        sql_prompt = [
            {"role": "system", "content": system_sql},
            {
                "role": "user",
                "content": f"User question:\n{question}\n\nDatabase schema (JSON):\n{schema_json}",
            },
        ]

        sql_raw = _chat(sql_prompt, temperature=0.0)
        sql_query = _extract_sql(sql_raw).strip()

        if not sql_query:
            return "⚠️ I could not generate a SQL query for that question."

        # 3) Run SQL safely
        try:
            df = run_sql(sql_query)
            table_md = df_to_markdown(df)
        except Exception as e:
            return f"⚠️ SQL execution error:\n\n```sql\n{sql_query}\n```\n\nError: `{e}`"

        # 4) Ask LLM to summarize the result
        system_ans = textwrap.dedent(
            """
            You are a senior data analyst.

            You will receive:
            - The original user question.
            - The SQL query used.
            - The query result table in markdown.

            TASK:
            - Briefly explain the answer in clear English.
            - Mention any key numbers or rankings.
            - If the table is empty or small, say that clearly.
            - DO NOT invent data that is not in the table.
            """
        )

        analysis_prompt = [
            {"role": "system", "content": system_ans},
            {
                "role": "user",
                "content": (
                    f"User question:\n{question}\n\n"
                    f"SQL query:\n```sql\n{sql_query}\n```\n\n"
                    f"Result table (markdown):\n{table_md}"
                ),
            },
        ]

        analysis = _chat(analysis_prompt, temperature=0.0)

        # 5) Final combined answer back to UI
        final_answer = (
            f"### 🔍 Question\n{question}\n\n"
            f"### 🧠 SQL Used\n```sql\n{sql_query}\n```\n\n"
            f"### 📊 Result (top rows)\n{table_md}\n\n"
            f"### 📈 Insight\n{analysis}"
        )

        return final_answer

    except Exception as e:
        # Always return a string – never None
        return f"[AGENT ERROR] {e}"
