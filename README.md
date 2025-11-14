# 🤖 Dumroo AI Developer

This project demonstrates an **AI-powered Admin Dashboard** where school administrators can ask **natural language questions** about student performance, homework submissions, and quizzes — powered by **LangChain + OpenAI** and a **Streamlit interface**.

---

## 🚀 Features

- **Natural Language Querying (NLQ)** — ask questions like:
  - “Which students haven’t submitted their homework yet?”
  - “Show me performance data for Grade 8 from last week.”
  - “List all upcoming quizzes scheduled for next week.”
- **Dual Query Modes:**
  - **Rule-based Parser (offline)** — fast keyword-based logic.
  - **OpenAI LLM Parser (online)** — intelligent understanding using GPT.
- **Role-based Filtering (AdminContext):**
  - Admins can be restricted by grade, class, and region.
- **Streamlit Web UI** with sidebar filters and query interface.
- **Default All-Data Mode** if no admin filters are selected.

---

## 🧩 Project Structure

```bash
dumroo-ai-assignment/
├─ data/
│  └─ students.csv
├─ ai_query.py
├─ app_streamlit.py
├─ utils.py
├─ requirements.txt
├─ .env
└─ README.md
```
---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/ManthanKaria/dumroo-ai.git
cd dumroo-ai-assignment
```

### 2️⃣ Create and Activate Virtual Environment

```bash
python -m venv dumroo_venv
```

Activate it:

```bash
dumroo_venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Create .env File

#### Create a new file named .env in the project root (dumroo-ai-assignment/.env):

```bash
OPENAI_API_KEY=sk-your_actual_api_key_here
```
#### #NoTE: Do not put the quotes over Key


### 5️⃣ Launch the App

```bash
streamlit run app_streamlit.py
```


### 🧠 How It Works
#### 🧩 Query Processing Flow

1) The admin enters a plain-English question.

2) Depending on the checkbox:

    - LLM Mode ON → OpenAI model (via LangChain) extracts intent & filters.

    - LLM Mode OFF → Rule-based parser extracts filters using keyword logic.

3) The system applies:

    - Admin Filters (Sidebar) → define what the admin is allowed to see (Grade/Class/Region).

    - Query Filters (Parsed) → define what the admin is asking about (e.g., “next week”, “Grade 8”).

4) Filtered data is displayed interactively in a Streamlit DataFrame.
