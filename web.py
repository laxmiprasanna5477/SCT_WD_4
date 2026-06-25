import streamlit as st
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="To-Do Web App", page_icon="📝", layout="wide")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
    <style>
        .main {
            background-color: #f5f7fb;
        }
        h1 {
            color: #111;
            text-align: center;
        }
        .task-box {
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
            color: black;
        }
        .completed {
            text-decoration: line-through;
            color: gray;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("📝 TO-DO WEB APP")

# ---------------- SESSION STATE ----------------
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# ---------------- ADD TASK ----------------
st.subheader("➕ Add New Task")

task = st.text_input("Task Name")
col1, col2 = st.columns(2)

with col1:
    date = st.date_input("Select Date")
with col2:
    time = st.time_input("Select Time")

if st.button("Add Task"):
    if task:
        st.session_state.tasks.append({
            "task": task,
            "date": str(date),
            "time": str(time),
            "done": False
        })
        st.success("Task Added Successfully!")

# ---------------- DISPLAY TASKS ----------------
st.subheader("📋 Your Tasks")

for i, t in enumerate(st.session_state.tasks):

    col1, col2, col3, col4 = st.columns([4, 2, 2, 2])

    with col1:
        if t["done"]:
            st.markdown(f"✔️ <span class='completed'>{t['task']}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"📝 {t['task']}", unsafe_allow_html=True)

    with col2:
        st.write(f"📅 {t['date']}")

    with col3:
        st.write(f"⏰ {t['time']}")

    with col4:
        if st.button("✅ Done", key=f"done{i}"):
            st.session_state.tasks[i]["done"] = True
            st.rerun()

        if st.button("❌ Delete", key=f"del{i}"):
            st.session_state.tasks.pop(i)
            st.rerun()

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("<p style='text-align:center;color:gray;'>Built with ❤️ using Streamlit</p>", unsafe_allow_html=True)