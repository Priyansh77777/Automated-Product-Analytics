# Automated Product Analytics: Natural Language SQL Agent

A Streamlit-based application that allows users to query product data using natural language. This project leverages LangChain and the Groq API to autonomously translate plain English business questions into executable SQL queries, bridging the gap between raw data and business insights without requiring users to write code.

## Project Overview

Product managers and analysts often need rapid answers from product datasets, but writing custom SQL queries for every ad-hoc question creates a reporting bottleneck. This system solves that problem by acting as an intelligent data assistant. Users can upload multiple CSV files, which the system dynamically converts into a structured SQLite database. An LLM-powered SQL agent then interprets user questions, writes the corresponding SQL, executes it against the database, and returns the final data.

## Key Features

* **Natural Language Querying:** Translate plain English questions (e.g., "What was the churn rate last month?" or "Show me top performing products by revenue") directly into accurate SQL queries.
* **Automated Database Generation:** Dynamically ingests multiple CSV uploads and structures them into a temporary, queryable SQLite database.
* **High-Speed Inference:** Utilizes the Groq API for near-instantaneous LLM reasoning and SQL generation.
* **Interactive UI:** Built with Streamlit for a clean, browser-based user experience.

## Technology Stack

* **Python:** Core application logic
* **Streamlit:** Frontend web interface
* **LangChain:** LLM orchestration and SQL agent framework
* **Groq API:** High-speed inference engine for natural language understanding
* **SQLite:** Lightweight relational database management
* **Pandas:** Data manipulation and CSV ingestion

## Repository Structure

```text
Automated-Product-Analytics/
│
├── app.py               # Main Streamlit application and LLM agent logic
├── requirements.txt     # Python dependencies
├── .gitignore           # Standard git ignore rules
└── README.md            # Project documentation

```

## Installation and Setup

### Prerequisites

* Python 3.8 or higher
* A valid Groq API key

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/Priyansh77777/Automated-Product-Analytics.git
cd Automated-Product-Analytics

```


2. **Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

```


3. **Install dependencies**
```bash
pip install -r requirements.txt

```


4. **Configure Environment Variables**
Set your Groq API key in your terminal or create a `.env` file in the root directory:
```bash
export GROQ_API_KEY="your_groq_api_key_here"

```


5. **Run the Application**
```bash
streamlit run app.py

```



## Usage

1. Launch the application using the Streamlit command.
2. Use the sidebar to upload one or more CSV datasets.
3. Once the data is processed into the SQLite database, use the chat interface to ask questions about your data in plain English.
4. The system will display the generated SQL query alongside the retrieved data.
