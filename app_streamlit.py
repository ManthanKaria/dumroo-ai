# app_streamlit.py
import streamlit as st
from utils import AdminContext, load_data
from ai_query import run_query

st.set_page_config(page_title="Dumroo Admin AI Demo", layout="wide")

st.title("Dumroo Admin Panel — Natural Language Query Demo")

# --- Admin context input (simulate logged-in admin) ---
with st.sidebar.form("admin_form"):
    st.header("Admin Context (simulate login)")
    admin_id = st.text_input("Admin ID", value="admin_123")
    allowed_grade = st.selectbox("Allowed Grade", options=["", "7", "8", "9"], index=2)
    allowed_class = st.selectbox("Allowed Class", options=["", "A", "B", "C"], index=1)
    allowed_region = st.selectbox("Allowed Region", options=["", "North", "South", "East", "West"], index=1)
    use_llm = st.checkbox("Use OpenAI LangChain parsing (requires OPENAI_API_KEY)", value=False)
    submitted = st.form_submit_button("Save Context")
if submitted:
    st.sidebar.success("Context saved")

admin_ctx = AdminContext(admin_id=admin_id, allowed_grade=allowed_grade or None, allowed_class=allowed_class or None, allowed_region=allowed_region or None)

st.sidebar.write("Current admin context:")
st.sidebar.write(admin_ctx)

# --- Input question ---
st.header("Ask a question (plain English)")
nl_query = st.text_area("Question", value="Which students haven’t submitted their homework yet?")

if st.button("Run Query"):
    if not nl_query.strip():
        st.error("Type a question first.")
    else:
        with st.spinner("Processing..."):
            try:
                result = run_query(nl_query, admin_ctx, use_llm=use_llm)
                st.subheader("Result")
                st.write("Intent:", result.get("intent"))
                st.write("Filters applied:", result.get("filters_applied"))
                if "count" in result:
                    st.write(f"Count: {result['count']}")
                rows = result.get("rows", [])
                if rows:
                    st.dataframe(rows)
                if "class_averages" in result:
                    st.subheader("Class Averages")
                    st.dataframe(result["class_averages"])
            except Exception as e:
                st.error(f"Error running query: {e}")
