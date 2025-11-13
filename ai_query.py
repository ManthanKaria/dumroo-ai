# ai_query.py
import os
import json
import re
from typing import Dict, Any
import pandas as pd
from datetime import date, timedelta

from dotenv import load_dotenv
load_dotenv()  # Load your .env file automatically

# ✅ Modern LangChain imports
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence

from utils import load_data, AdminContext, apply_scope_filter


# ---------- Environment Setup ----------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# ---------- Prompt Template ----------
PARSER_PROMPT = """
You are a JSON extractor. Given an admin's plain-English query about students/quizzes/homework,
output a JSON object with keys:
- intent: one of ["list_homework_pending", "show_performance", "list_upcoming_quizzes", "other"]
- filters: a dict possibly containing keys "grade", "class", "region", "date_from", "date_to", "quiz_name", "week"
- metrics: what metric to show (e.g., "quiz_score", "homework_submitted")
- raw_query: the original question

If you cannot parse, set intent to "other" and include raw_query.

Return ONLY valid JSON.

Query: \"\"\"{query}\"\"\"
"""


# ---------- Function: Parse query with LLM ----------
def parse_with_llm(query: str) -> Dict[str, Any]:
    """Parse a natural-language query into structured JSON using OpenAI via LangChain."""
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY missing; cannot run LLM parsing.")

    llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)
    prompt = PromptTemplate(template=PARSER_PROMPT, input_variables=["query"])
    parser = StrOutputParser()

    chain = RunnableSequence(prompt | llm | parser)
    resp = chain.invoke({"query": query})

    # Extract JSON substring from response
    try:
        start = resp.find('{')
        end = resp.rfind('}')
        js = resp[start:end + 1]
        parsed = json.loads(js)
        return parsed
    except Exception as e:
        raise RuntimeError(f"Failed to parse LLM response into JSON. raw_resp={resp!r} error={e}")


# ---------- Simple Rule-Based Fallback Parser ----------
def simple_rule_parse(query: str) -> Dict[str, Any]:
    q = query.lower()
    intent = "other"
    filters = {}
    metrics = None

    # grade/class/region extraction
    grade_match = re.search(r"grade\s*(\d+)", q)
    if grade_match:
        filters["grade"] = grade_match.group(1)

    class_match = re.search(r"class\s*([A-Z0-9])", query, re.I)
    if class_match:
        filters["class"] = class_match.group(1).upper()

    region_match = re.search(r"(north|south|east|west|central|region\s*[:\-]?\s*(\w+))", q, re.I)
    if region_match:
        filters["region"] = region_match.group(1).split()[-1].capitalize()

    # date ranges
    if "last week" in q:
        filters["week"] = "last"
    if "next week" in q:
        filters["week"] = "next"

    if any(x in q for x in ["haven't submitted", "not submitted", "homework pending", "homework not"]):
        intent = "list_homework_pending"
        metrics = "homework_submitted"
    elif any(x in q for x in ["performance", "scores", "average", "show me performance"]):
        intent = "show_performance"
        metrics = "quiz_score"
    elif any(x in q for x in ["upcoming quiz", "upcoming quizzes", "next week quiz"]):
        intent = "list_upcoming_quizzes"
    elif "list" in q and "quiz" in q:
        intent = "list_upcoming_quizzes"
    elif "who" in q and "homework" in q:
        intent = "list_homework_pending"

    return {"intent": intent, "filters": filters, "metrics": metrics, "raw_query": query}


# ---------- Main Query Execution ----------
def run_query(nl_query: str, admin_ctx: AdminContext, use_llm: bool = True) -> Dict[str, Any]:
    """Execute a natural-language admin query and return structured results."""
    df = load_data()
    scoped_df = apply_scope_filter(df, admin_ctx)

    # Parse user question
    if use_llm:
        try:
            parsed = parse_with_llm(nl_query)
        except Exception as e:
            print(f"LLM parse failed ({e}). Falling back to simple parser.")
            parsed = simple_rule_parse(nl_query)
    else:
        parsed = simple_rule_parse(nl_query)

    intent = parsed.get("intent", "other")
    filters = parsed.get("filters", {}) or {}

    # Apply any explicit filters
    df2 = scoped_df.copy()
    if "grade" in filters:
        df2 = df2[df2["grade"].astype(str) == str(filters["grade"])]
    if "class" in filters:
        df2 = df2[df2["class"].astype(str).str.upper() == str(filters["class"]).upper()]
    if "region" in filters:
        df2 = df2[df2["region"].astype(str).str.lower() == str(filters["region"]).lower()]

    result = {"intent": intent, "query": nl_query, "filters_applied": filters}

    # ---------- Handle each intent ----------
    if intent == "list_homework_pending":
        pending = df2[df2["homework_submitted"] == False]
        result["count"] = len(pending)
        result["rows"] = pending.to_dict(orient="records")
        return result

    if intent == "show_performance":
        result["rows"] = df2[
            ["student_id", "student_name", "grade", "class", "quiz_name", "quiz_date", "quiz_score"]
        ].to_dict(orient="records")
        avg_by_class = (
            df2.groupby(["grade", "class"])["quiz_score"]
            .mean()
            .reset_index()
            .rename(columns={"quiz_score": "avg_quiz_score"})
        )
        result["class_averages"] = avg_by_class.to_dict(orient="records")
        return result

    if intent == "list_upcoming_quizzes":
        today = pd.to_datetime(date.today())
        if filters.get("week") == "next":
            start = today + timedelta(days=1)
            end = start + timedelta(days=7)
            upcoming = df2[(df2["quiz_date"] >= start) & (df2["quiz_date"] <= end)]
        else:
            upcoming = df2[df2["quiz_date"] >= today]
        result["rows"] = (
            upcoming[["quiz_name", "quiz_date", "grade", "class", "student_name"]]
            .sort_values("quiz_date")
            .to_dict(orient="records")
        )
        return result

    # ---------- Fallback ----------
    result["note"] = "Intent not recognized; returning scoped sample data."
    result["rows"] = df2.head(10).to_dict(orient="records")
    return result


# ---------- CLI Testing ----------
if __name__ == "__main__":
    ctx = AdminContext(admin_id="admin_123", allowed_grade="8", allowed_class="A", allowed_region="North")
    q = "Which students haven’t submitted their homework yet?"
    print(run_query(q, ctx, use_llm=False))
