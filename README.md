# Automated Product Analytics: Natural Language SQL Agent

A Streamlit-based application that allows users to explore structured datasets using natural language. Built with Python, LangChain, the Groq API and SQLite, the application uses an LLM-powered SQL agent to translate business questions into SQL queries, execute them against selected database tables, and return data-backed answers.

## Project Overview

Product managers and analysts frequently need answers to ad-hoc questions about business data. Writing SQL for every request can slow down exploratory analysis, particularly for users who are not comfortable querying databases directly.

This project provides an interactive data assistant that supports CSV ingestion, local SQLite storage and natural-language querying. Users can upload multiple CSV files, select the tables they want to query, and ask questions through a Streamlit chat interface. The SQL agent uses database schema information and available SQL tools to generate and execute queries, then returns a response based on the query results.

The application also maintains chat history within the Streamlit session and provides access to intermediate agent steps for inspecting the generated SQL and database outputs.

## Key Features

- **Natural-Language SQL Querying:** Ask analytical questions in plain English and use an LLM-powered SQL agent to query selected database tables.
- **Multi-CSV Ingestion:** Upload multiple CSV files in one workflow and load their contents into SQLite tables.
- **Table Selection:** Select which available tables should be included in the SQL agent's database context.
- **Interactive Chat Interface:** Explore datasets through a Streamlit interface with recent chat history and suggested queries.
- **Query Inspection:** Inspect intermediate agent steps, including tool inputs and database outputs, to help understand how a response was produced.
- **Local Relational Storage:** Store and query uploaded datasets using SQLite.

## Technology Stack

- **Python:** Application logic and data processing
- **Streamlit:** Interactive web interface
- **LangChain:** SQL agent orchestration and database-tool integration
- **Groq API:** LLM inference using the configured `openai/gpt-oss-120b` model
- **SQLite:** Relational storage and SQL execution
- **Pandas:** CSV ingestion and conversion into database tables
- **python-dotenv:** Loading environment variables from a `.env` file

## Repository Structure

```text
Automated-Product-Analytics/
├── app.py               # Streamlit application, CSV ingestion, chat UI and SQL agent
├── sql_agent.py         # Standalone command-line SQL agent
├── setup_db.py          # Script to load ecommerce_data.csv into SQLite
├── product_metrics.db   # SQLite database, if included in the repository
├── requirements.txt     # Python dependencies
├── .gitignore           # Git ignore rules
└── README.md            # Project documentation
```

The `setup_db.py` script expects an `ecommerce_data.csv` file in the same directory. Ensure that this input file is available if you intend to run the setup script.

## Installation and Setup

### Prerequisites

- Python 3.8 or higher, subject to the installed dependency versions
- A valid Groq API key

### 1. Clone the repository

```bash
git clone https://github.com/Priyansh77777/Automated-Product-Analytics.git
cd Automated-Product-Analytics
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On macOS or Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Groq API key

Create a `.env` file in the project root:

```text
GROQ_API_KEY=your_groq_api_key_here
```

Keep the API key private and do not commit it to version control.

### 5. Run the Streamlit application

```bash
streamlit run app.py
```

## Usage

1. Launch the application in your browser.
2. Upload one or more CSV files using the sidebar.
3. Select the database tables you want the agent to query.
4. Enter a natural-language question in the chat interface or use a suggested query.
5. Review the response returned by the agent.
6. Expand the SQL inspection panel to examine intermediate tool inputs and database outputs.
7. Use the sidebar to revisit recent chats, start a new chat or delete a dataset.

## Implementation Notes and Limitations

- Uploaded CSV data is written to `product_metrics.db`, a local SQLite database file. The database is not automatically temporary or deleted when a chat session ends.
- CSV uploads create or replace tables using names derived from the uploaded filenames. Uploading a file with the same derived table name can replace an existing table.
- Chat history is stored in Streamlit session state; it is not a durable, multi-user conversation store.
- The SQL agent's output depends on the uploaded data, database schema, generated SQL and model response. A successful query execution does not by itself guarantee that the answer matches the intended business definition.
- The application should be treated as a local analytics prototype rather than a production-grade, multi-user analytics platform.

## Future Improvements

- Add stricter read-only SQL validation and database access controls.
- Improve upload validation, table-name collision handling and data-quality checks.
- Evaluate SQL correctness using a benchmark of representative business questions.
- Add structured KPI definitions and clearer handling of ambiguous requests.
- Benchmark ingestion time, query execution time and end-to-end response latency across different dataset sizes.
- Improve error handling, logging and persistence of chat history.
