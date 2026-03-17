import streamlit as st
import sqlite3
from datetime import datetime
import requests
import bcrypt

st.set_page_config(page_title="AI Life System", page_icon="🚀")

# ================= DATABASE =================
conn = sqlite3.connect("planner.db", check_same_thread=False)
cursor = conn.cursor()

# TABLES
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password BLOB
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS study_logs (
    username TEXT,
    day TEXT,
    subject TEXT,
    topic TEXT,
    subtopic TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS water_logs (
    username TEXT,
    day TEXT,
    amount REAL,
    time TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS food_logs (
    username TEXT,
    day TEXT,
    morning TEXT,
    breakfast TEXT,
    snack1 TEXT,
    lunch TEXT,
    snack2 TEXT,
    dinner TEXT,
    time TEXT
)
""")

# ================= AI =================
def ask_ai(prompt):
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        })
        return response.json()["response"]
    except:
        return "⚠️ AI not running. Start Ollama."

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None

# ================= LOGIN / SIGNUP =================
if st.session_state.user is None:
    st.title("🔐 Login / Signup")

    option = st.selectbox("Choose", ["Login", "Signup"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # ===== SIGNUP =====
    if option == "Signup":
        if st.button("Create Account"):
            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            if cursor.fetchone():
                st.error("User already exists!")
            else:
                hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                cursor.execute("INSERT INTO users VALUES (?, ?)", (username, hashed_password))
                conn.commit()
                st.success("Account created! Now login.")

    # ===== LOGIN =====
    if option == "Login":
        if st.button("Login"):
            cursor.execute("SELECT password FROM users WHERE username=?", (username,))
            result = cursor.fetchone()

            if result and bcrypt.checkpw(password.encode(), result[0]):
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid credentials")

# ================= MAIN APP =================
else:
    user = st.session_state.user

    # ✅ Welcome message
    st.title(f"Hi {user} 👋")

    # Sidebar menu
    option = st.sidebar.selectbox("Select Module", ["Study", "Water", "Food", "Analysis", "Logout"])

    # ================= STUDY =================
    if option == "Study":
        st.header("📚 Study Tracker")

        selected_date = st.date_input("📅 Select Date")
        formatted_date = selected_date.strftime("%d-%m-%Y")

        subject = st.text_input("Subject")
        topic = st.text_input("Topic")
        subtopic = st.text_input("Subtopic")

        if st.button("Save Study"):
            cursor.execute("INSERT INTO study_logs VALUES (?, ?, ?, ?, ?)",
                           (user, formatted_date, subject, topic, subtopic))
            conn.commit()
            st.success("Study Saved!")

    # ================= WATER =================
    elif option == "Water":
        st.header("💧 Water Tracker")

        amount = st.number_input("Water (liters)", 0.0, 5.0)

        if st.button("Add Water"):
            cursor.execute("INSERT INTO water_logs VALUES (?, ?, ?, ?)",
                           (user,
                            datetime.now().strftime("%d-%m-%Y"),
                            amount,
                            datetime.now().strftime("%H:%M")))
            conn.commit()
            st.success("Water Added!")

    # ================= FOOD =================
    elif option == "Food":
        st.header("🍽️ Food Tracker")

        morning = st.text_input("☕ Morning Drink")
        breakfast = st.text_input("🍳 Breakfast")
        snack1 = st.text_input("🍪 Snack 1")
        lunch = st.text_input("🍛 Lunch")
        snack2 = st.text_input("🍫 Snack 2")
        dinner = st.text_input("🍽️ Dinner")

        if st.button("Save Food"):
            cursor.execute("INSERT INTO food_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (user,
                            datetime.now().strftime("%d-%m-%Y"),
                            morning, breakfast, snack1, lunch, snack2, dinner,
                            datetime.now().strftime("%H:%M")))
            conn.commit()
            st.success("Food Saved!")

    # ================= ANALYSIS =================
    elif option == "Analysis":
        st.header("🧠 AI Analysis")

        analysis_type = st.selectbox("Select Type", ["Daily", "Weekly", "Monthly"])

        cursor.execute("SELECT * FROM study_logs WHERE username=?", (user,))
        study = cursor.fetchall()

        cursor.execute("SELECT * FROM water_logs WHERE username=?", (user,))
        water = cursor.fetchall()

        cursor.execute("SELECT * FROM food_logs WHERE username=?", (user,))
        food = cursor.fetchall()

        if st.button("Analyze"):
            prompt = f"""
You are a strict personal coach.

User: {user}

Study:
{study}

Water:
{water}

Food:
{food}

Give {analysis_type} analysis:
- mistakes
- habits
- improvements
- plan
"""

            result = ask_ai(prompt)
            st.write(result)

    # ================= LOGOUT =================
    elif option == "Logout":
        st.session_state.user = None
        st.rerun()