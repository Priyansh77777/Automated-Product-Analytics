import os
import time
import sqlite3
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent

# 1. Page Configuration & Gemini-Style CSS
st.set_page_config(page_title="AI Data Copilot", page_icon="✨", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    header {background: transparent !important;}
    
    [data-testid="stAppViewContainer"] { background-color: #131314; }
    [data-testid="stSidebar"] {
        background-color: #1e1f20;
        border-right: 1px solid #282a2c;
    }

    html, body, [class*="css"] { font-family: 'Google Sans', 'Inter', sans-serif; }
    div[data-testid="metric-container"] {
        background-color: #1a1a1c; border: 1px solid #2e2e2e;
        padding: 5% 10%; border-radius: 8px;
    }

    /* New Chat Button */
    .st-key-new_chat_btn > button {
        background-color: #1a1a1c !important; color: #e3e3e3 !important;
        border: 1px solid #3c4043 !important; border-radius: 24px !important;
        font-weight: 500 !important; padding: 8px 18px !important; margin-bottom: 12px !important;
        display: flex !important; justify-content: flex-start !important;
    }
    .st-key-new_chat_btn > button:hover { background-color: #282a2c !important; color: #ffffff !important; }

    /* Sidebar History Items */
    [data-testid="stSidebar"] .stButton > button {
        border: none !important; border-radius: 24px !important; padding: 8px 14px !important;
        height: 38px !important; width: 100% !important; display: flex !important;
        justify-content: flex-start !important; text-align: left !important;
        background: transparent !important; color: #c4c7c5 !important;
    }
    [data-testid="stSidebar"] .stButton > button div, [data-testid="stSidebar"] .stButton > button p {
        white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important;
        width: 100% !important; margin: 0 !important; font-size: 0.875rem !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover { background-color: #282a2c !important; color: #ffffff !important; }
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: #282a2d !important; color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

load_dotenv()
DB_FILE = "product_metrics.db"

# --- SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state: st.session_state.messages = []
if "ingested_files" not in st.session_state: st.session_state.ingested_files = set()
if "chat_history" not in st.session_state: st.session_state.chat_history = {} 
if "current_chat_title" not in st.session_state: st.session_state.current_chat_title = None

# 2. Sidebar Logic
with st.sidebar:
    # 1. Fetch tables FIRST so the New Chat / History buttons can access the schema
    active_tables = []
    if os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        active_tables = [row[0] for row in cursor.fetchall()]
        conn.close()

    # Sync Multiselect widget state
    if "selected_tables_widget" not in st.session_state:
        st.session_state.selected_tables_widget = active_tables.copy()
    else:
        st.session_state.selected_tables_widget = [t for t in st.session_state.selected_tables_widget if t in active_tables]

    # 2. New Chat Button
    if st.button("＋  New chat", key="new_chat_btn", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_chat_title = None
        st.session_state.selected_tables_widget = active_tables.copy()
        st.rerun()
        
    # 3. Recent Chats Loop
    if st.session_state.chat_history:
        st.markdown("<p style='font-size: 0.8rem; color: #8e918f; font-weight: 500; margin: 16px 0 6px 12px;'>Recent</p>", unsafe_allow_html=True)
        
        for title in reversed(list(st.session_state.chat_history.keys())):
            is_active = (title == st.session_state.current_chat_title)
            btn_type = "primary" if is_active else "secondary"
            
            if st.button(title, key=f"hist_{title}", use_container_width=True, type=btn_type):
                chat_data = st.session_state.chat_history[title]
                
                # Backward compatibility check for older saved chats
                if isinstance(chat_data, list):
                    st.session_state.messages = chat_data.copy()
                    st.session_state.selected_tables_widget = active_tables.copy()
                else:
                    st.session_state.messages = chat_data["messages"].copy()
                    # Magically restore the exact multiselect tables used in this historical chat!
                    st.session_state.selected_tables_widget = [t for t in chat_data.get("tables", []) if t in active_tables]
                
                st.session_state.current_chat_title = title
                st.rerun()
                
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("### 🗂️ Data Context")
    
    # 4. File Uploader
    uploaded_files = st.file_uploader("Upload CSV", type=["csv"], accept_multiple_files=True, label_visibility="collapsed")
    if uploaded_files:
        new_files = [f for f in uploaded_files if f.name not in st.session_state.ingested_files]
        if new_files:
            conn = sqlite3.connect(DB_FILE)
            for file in new_files:
                table_name = os.path.splitext(file.name)[0].strip().replace(" ", "_").replace("-", "_")
                df = pd.read_csv(file)
                df.to_sql(table_name, conn, if_exists="replace", index=False)
                st.session_state.ingested_files.add(file.name)
            conn.close()
            st.success(f"Added {len(new_files)} file(s).")
            # Force widget reset on new upload
            if "selected_tables_widget" in st.session_state:
                del st.session_state["selected_tables_widget"]
            time.sleep(1) 
            st.rerun()
            
    # 5. Table Multiselect (Now strictly bound to st.session_state.selected_tables_widget)
    selected_tables = []
    if active_tables:
        st.markdown("**Active Tables:**")
        selected_tables = st.multiselect(
            "Select tables to query", 
            options=active_tables, 
            key="selected_tables_widget", 
            label_visibility="collapsed"
        )
        
        with st.expander("🗑️ Delete Datasets"):
            for t in active_tables:
                col1, col2 = st.columns([3, 1])
                col1.caption(t)
                if col2.button("✖", key=f"del_{t}"):
                    conn = sqlite3.connect(DB_FILE)
                    conn.cursor().execute(f'DROP TABLE "{t}"')
                    conn.commit()
                    conn.close()
                    st.session_state.ingested_files = {f for f in st.session_state.ingested_files if not f.startswith(t)}
                    if "selected_tables_widget" in st.session_state: del st.session_state["selected_tables_widget"]
                    st.rerun()

# 3. Main Dashboard Layout
st.title("✨ AI Data Copilot")
st.markdown("**Autonomous SQL Agent** • Powered by Llama 3 & LangGraph")
st.divider()

def get_agent_executor(tables_to_include):
    db = SQLDatabase.from_uri(f"sqlite:///{DB_FILE}", include_tables=tables_to_include)
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"))
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    return create_sql_agent(llm=llm, toolkit=toolkit, verbose=True, agent_type="tool-calling", return_intermediate_steps=True)

# 4. Zero-State Onboarding
if len(st.session_state.messages) == 0:
    st.markdown("### 👋 Welcome back.")
    st.caption("Select a suggested query based on your active data context, or ask your own.")
    st.write("")
    if selected_tables:
        col1, col2, col3 = st.columns(3)
        t1 = selected_tables[0]
        with col1:
            if st.button(f"🔍 **Explore {t1}**\n\nHow many total rows are in the {t1} table?", use_container_width=True):
                st.session_state.current_chat_title = f"Explore {t1}"
                st.session_state.messages.append({"role": "user", "content": f"How many total rows are in the {t1} table?"})
                st.session_state.chat_history[st.session_state.current_chat_title] = {"messages": st.session_state.messages.copy(), "tables": list(selected_tables)}
                st.rerun()
        with col2:
            if st.button(f"📊 **Analyze {t1}**\n\nWhat are the top 3 most common values in the {t1} table?", use_container_width=True):
                st.session_state.current_chat_title = f"Analyze {t1}"
                st.session_state.messages.append({"role": "user", "content": f"What are the top 3 most common values in the {t1} table?"})
                st.session_state.chat_history[st.session_state.current_chat_title] = {"messages": st.session_state.messages.copy(), "tables": list(selected_tables)}
                st.rerun()
        if len(selected_tables) > 1:
            t2 = selected_tables[1]
            with col3:
                if st.button(f"🔗 **Cross-check {t2}**\n\nShow me a brief summary of the {t2} table.", use_container_width=True):
                    st.session_state.current_chat_title = f"Summary of {t2}"
                    st.session_state.messages.append({"role": "user", "content": f"Show me a brief summary of the {t2} table."})
                    st.session_state.chat_history[st.session_state.current_chat_title] = {"messages": st.session_state.messages.copy(), "tables": list(selected_tables)}
                    st.rerun()
        else:
            with col3:
                if st.button("💡 **General Quality**\n\nAre there any missing or null values in the database?", use_container_width=True):
                    st.session_state.current_chat_title = "Data Quality Check"
                    st.session_state.messages.append({"role": "user", "content": "Are there any missing or null values in the database?"})
                    st.session_state.chat_history[st.session_state.current_chat_title] = {"messages": st.session_state.messages.copy(), "tables": list(selected_tables)}
                    st.rerun()
    else:
        st.info("👈 Please upload and select a CSV dataset in the sidebar to get started.")

# Render history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "latency" in msg: st.caption(f"⏱️ **Execution Latency:** {msg['latency']:.2f}s")
        if "debug_steps" in msg and msg["debug_steps"]:
            with st.expander("🔍 Inspect Agent Thought Process & SQL"):
                st.code(msg["debug_steps"], language="sql")

# 5. Query Execution Loop
if prompt := st.chat_input("Ask a question about your selected datasets..."):
    if not st.session_state.current_chat_title:
        st.session_state.current_chat_title = prompt[:25] + "..." if len(prompt) > 25 else prompt
        
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Save both messages AND the currently active tables to the chat history dict
    st.session_state.chat_history[st.session_state.current_chat_title] = {
        "messages": st.session_state.messages.copy(),
        "tables": list(selected_tables)
    }
    st.rerun()

if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    user_prompt = st.session_state.messages[-1]["content"]
    hidden_instruction = " (Note: In your final response, explicitly state the exact table name(s) you queried.)"
    enhanced_prompt = user_prompt + hidden_instruction
    
    with st.chat_message("assistant"):
        if not selected_tables:
            st.error("Please select at least one dataset in the sidebar to query.")
            st.stop()
            
        with st.spinner("Analyzing schema and compiling SQL..."):
            start_time = time.time()
            try:
                agent_executor = get_agent_executor(selected_tables)
                result = agent_executor.invoke({"input": enhanced_prompt})
                latency = time.time() - start_time
                answer = result.get("output", str(result))
                
                debug_log = ""
                if "intermediate_steps" in result:
                    for action, observation in result["intermediate_steps"]:
                        debug_log += f"-- Action: {action.tool}\n-- Query Compiled:\n{action.tool_input}\n-- Database Output:\n{observation}\n\n"

                st.markdown(answer)
                st.caption(f"⏱️ **Execution Latency:** {latency:.2f}s")
                if debug_log:
                    with st.expander("🔍 Inspect Agent Thought Process & SQL"): st.code(debug_log, language="sql")

                st.session_state.messages.append({
                    "role": "assistant", "content": answer, "latency": latency, "debug_steps": debug_log
                })
                
                st.session_state.chat_history[st.session_state.current_chat_title] = {
                    "messages": st.session_state.messages.copy(),
                    "tables": list(selected_tables)
                }
            except Exception as e:
                st.error(f"Execution Error: {e}")