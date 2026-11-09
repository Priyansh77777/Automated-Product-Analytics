"""Interactive SQL chat agent for product_metrics.db."""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "product_metrics.db"

load_dotenv(BASE_DIR / ".env")

db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH.as_posix()}")

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    groq_api_key=os.getenv("GROQ_API_KEY"),
)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type="tool-calling",
)

while True:
    question = input("Ask a question about the product metrics: ").strip()
    if question.lower() in {"quit", "exit"}:
        break
    if not question:
        continue
    result = agent_executor.invoke({"input": question})
    print(result.get("output", result))
