import streamlit as st
import sqlite3
from datetime import datetime
import openai

# ================= CONFIG =================
st.set_page_config(page_title="AI Life System", page_icon="🧠")

# 👉 Add your OpenAI API key in Streamlit secrets (IMPORTANT)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ================= DATABASE =================
conn = sqlite3.connect("planner.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS study_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    activity TEXT,
    created_at TEXT
)
""")
conn.commit()

# ================= SIDEBAR =================
st.sidebar.title("📌 Menu")
module = st.sidebar.selectbox("Select Module", ["Analysis", "Logs"])

# ================= FUNCTIONS =================
def get_ai_analysis(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful productivity assistant."},
                {"role": "user", "content": text}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {e}"

# ================= MAIN =================
st.title("Hi Aishu 👋")
st.header("🧠 AI Analysis")

if module == "Analysis":
    analysis_type = st.selectbox("Select Type", ["Daily", "Weekly"])

    user_input = st.text_area("Describe your day / activities")

    if st.button("Analyze"):
        if user_input.strip() == "":
            st.warning("Please enter something to analyze")
        else:
            with st.spinner("Analyzing..."):
                result = get_ai_analysis(user_input)

                st.success("Analysis Complete ✅")
                st.write(result)

                # Save to DB
                cursor.execute(
                    "INSERT INTO study_logs (username, activity, created_at) VALUES (?, ?, ?)",
                    ("Aishu", user_input, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                conn.commit()

elif module == "Logs":
    st.subheader("📊 Past Logs")

    cursor.execute("SELECT * FROM study_logs ORDER BY id DESC")
    data = cursor.fetchall()

    if data:
        for row in data:
            st.write(f"🗓 {row[3]}")
            st.write(f"📝 {row[2]}")
            st.markdown("---")
    else:
        st.info("No logs yet")
