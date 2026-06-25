"""
==========================================================
 Smart To-Do Manager — Web Application
 Built using Python + Streamlit + Pandas
==========================================================
Features:
 - Add / Edit / Delete tasks
 - Mark tasks Completed / Pending
 - Due Date + Due Time, Priority, Category
 - Dashboard with Total / Completed / Pending / % stats
 - Sidebar filters (status, category, priority) + search
 - Local CSV storage, auto-saved on every change
 - Overdue task warnings
 - Progress bar, CSV download, clear-completed button
 - Duplicate task prevention using session_state
==========================================================
Run with:
    streamlit run app.py
==========================================================
"""

import os
from datetime import datetime, date, time as dtime

import pandas as pd
import streamlit as st

# ----------------------------------------------------------------
# APP CONFIGURATION
# ----------------------------------------------------------------
st.set_page_config(
    page_title="✅ Smart To-Do Manager",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_TITLE = "Smart To-Do Manager"
TASKS_FILE = "tasks.csv"
CATEGORIES = ["Study", "Personal", "Work", "Other"]
PRIORITIES = ["High", "Medium", "Low"]
STATUSES = ["Pending", "Completed"]

# Columns used in the CSV / DataFrame for every task
COLUMNS = [
    "ID", "Title", "Description", "Category", "Priority",
    "DueDate", "DueTime", "Status", "CreatedAt",
]

# ----------------------------------------------------------------
# CUSTOM CSS — MODERN, ATTRACTIVE, RESPONSIVE LOOK
# ----------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #141e30 0%, #243b55 100%);
    }
    .app-title {
        text-align: center;
        color: #ffffff;
        font-size: 2.3rem;
        font-weight: 800;
        margin-bottom: 0.1rem;
    }
    .app-subtitle {
        text-align: center;
        color: #c9d6df;
        font-size: 1rem;
        margin-bottom: 1.2rem;
    }
    .task-card {
        background: rgba(255,255,255,0.07);
        border-radius: 14px;
        padding: 16px 20px;
        border-left: 6px solid #4ecdc4;
        margin-bottom: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    .task-card.completed { border-left-color: #2ecc71; opacity: 0.75; }
    .task-card.overdue { border-left-color: #ff4d4d; }
    .task-title { font-size: 1.15rem; font-weight: 800; color: #ffffff; }
    .task-desc { color: #d6dde2; font-size: 0.92rem; margin-top: 2px; }
    .task-meta { color: #aab8c2; font-size: 0.82rem; margin-top: 6px; }
    .badge {
        display: inline-block; padding: 3px 10px; border-radius: 12px;
        font-size: 0.75rem; font-weight: 700; margin-right: 6px; color: #1f1c2c;
    }
    .badge-high { background: #ff6b6b; }
    .badge-medium { background: #ffd166; }
    .badge-low { background: #06d6a0; }
    .badge-cat { background: #74c0fc; }
    .badge-done { background: #2ecc71; color: #fff; }
    .badge-pending { background: #f1c40f; }
    .badge-overdue { background: #ff4d4d; color: #fff; }
    div.stButton > button {
        border-radius: 10px;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------
# DATA PERSISTENCE — load / save tasks to a local CSV file
# ----------------------------------------------------------------
def load_tasks() -> pd.DataFrame:
    """Load tasks from the local CSV file. Create an empty file/frame if absent or corrupt."""
    if os.path.exists(TASKS_FILE):
        try:
            df = pd.read_csv(TASKS_FILE, dtype={"ID": int})
            # Make sure every expected column exists (handles older/partial CSVs gracefully)
            for col in COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            return df[COLUMNS]
        except Exception:
            # Corrupt or unreadable file — start fresh rather than crashing the app
            return pd.DataFrame(columns=COLUMNS)
    return pd.DataFrame(columns=COLUMNS)


def save_tasks(df: pd.DataFrame):
    """Persist the current tasks DataFrame to the local CSV file."""
    try:
        df.to_csv(TASKS_FILE, index=False)
    except Exception as e:
        st.error(f"Could not save tasks to file: {e}")


# ----------------------------------------------------------------
# SESSION STATE INITIALIZATION
# ----------------------------------------------------------------
if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()          # Load once when the app starts
if "editing_id" not in st.session_state:
    st.session_state.editing_id = None             # Which task (ID) is currently being edited
if "flash_message" not in st.session_state:
    st.session_state.flash_message = None          # (type, text) shown once after an action


def flash(msg_type: str, text: str):
    """Queue a one-time success/info/error message to display after rerun."""
    st.session_state.flash_message = (msg_type, text)


def show_flash():
    """Display and clear any pending flash message."""
    if st.session_state.flash_message:
        msg_type, text = st.session_state.flash_message
        getattr(st, msg_type)(text)
        st.session_state.flash_message = None


# ----------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------
def get_next_id(df: pd.DataFrame) -> int:
    """Generate the next unique task ID."""
    if df.empty:
        return 1
    return int(df["ID"].max()) + 1


def is_duplicate_task(df: pd.DataFrame, title: str, category: str, exclude_id=None) -> bool:
    """
    Prevent duplicate task creation: a duplicate is the same title (case-insensitive)
    within the same category, excluding the task currently being edited (if any).
    """
    if df.empty:
        return False
    mask = (
        (df["Title"].astype(str).str.strip().str.lower() == title.strip().lower())
        & (df["Category"] == category)
    )
    if exclude_id is not None:
        mask &= df["ID"] != exclude_id
    return mask.any()


def combine_due_datetime(due_date, due_time):
    """Combine a date and time object into a single datetime for overdue comparisons."""
    try:
        return datetime.combine(due_date, due_time)
    except Exception:
        return None


def is_overdue(row) -> bool:
    """Check if a pending task's due date/time has already passed."""
    if row["Status"] == "Completed":
        return False
    try:
        due_date = datetime.strptime(str(row["DueDate"]), "%Y-%m-%d").date()
        due_time = datetime.strptime(str(row["DueTime"]), "%H:%M:%S").time()
        due_dt = combine_due_datetime(due_date, due_time)
        return due_dt is not None and due_dt < datetime.now()
    except Exception:
        # Gracefully handle malformed/missing date-time values
        return False


def priority_badge(priority: str) -> str:
    cls = {"High": "badge-high", "Medium": "badge-medium", "Low": "badge-low"}.get(priority, "badge-medium")
    return f'<span class="badge {cls}">{priority}</span>'


def status_badge(status: str, overdue: bool) -> str:
    if overdue:
        return '<span class="badge badge-overdue">⚠ OVERDUE</span>'
    cls = "badge-done" if status == "Completed" else "badge-pending"
    return f'<span class="badge {cls}">{status}</span>'


# ----------------------------------------------------------------
# SIDEBAR — filters + search + summary
# ----------------------------------------------------------------
def render_sidebar(df: pd.DataFrame):
    st.sidebar.title(f"✅ {APP_TITLE}")
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Search")
    search_term = st.sidebar.text_input("Search by title or description", value="")

    st.sidebar.subheader("🗂️ Filters")
    status_filter = st.sidebar.selectbox("View", ["All Tasks", "Completed Tasks", "Pending Tasks", "High Priority Tasks"])
    category_filter = st.sidebar.selectbox("Category", ["All Categories"] + CATEGORIES)

    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Clear All Completed Tasks", use_container_width=True):
        before = len(df)
        df = df[df["Status"] != "Completed"].reset_index(drop=True)
        st.session_state.tasks = df
        save_tasks(df)
        removed = before - len(df)
        flash("success", f"Cleared {removed} completed task(s).")
        st.rerun()

    if not df.empty:
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.sidebar.download_button(
            "⬇️ Download Tasks as CSV",
            data=csv_bytes,
            file_name="tasks_export.csv",
            mime="text/csv",
            use_container_width=True,
        )

    return search_term, status_filter, category_filter


# ----------------------------------------------------------------
# DASHBOARD — total / completed / pending / completion %
# ----------------------------------------------------------------
def render_dashboard(df: pd.DataFrame):
    total = len(df)
    completed = int((df["Status"] == "Completed").sum()) if total else 0
    pending = total - completed
    pct = round((completed / total) * 100, 1) if total > 0 else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📋 Total Tasks", total)
    col2.metric("✅ Completed", completed)
    col3.metric("⏳ Pending", pending)
    col4.metric("📊 Completion", f"{pct}%")

    st.progress(pct / 100, text=f"Overall Completion: {pct}%")

    # Overdue warning banner
    if total:
        overdue_df = df[df.apply(is_overdue, axis=1)]
        if not overdue_df.empty:
            overdue_titles = ", ".join(overdue_df["Title"].astype(str).tolist())
            st.warning(f"⚠️ You have {len(overdue_df)} overdue task(s): {overdue_titles}")

    st.markdown("---")


# ----------------------------------------------------------------
# ADD TASK FORM
# ----------------------------------------------------------------
def render_add_task_form():
    with st.expander("➕ Add New Task", expanded=False):
        with st.form("add_task_form", clear_on_submit=True):
            title = st.text_input("Task Title *")
            description = st.text_area("Task Description")

            c1, c2, c3 = st.columns(3)
            with c1:
                category = st.selectbox("Category", CATEGORIES)
            with c2:
                priority = st.selectbox("Priority Level", PRIORITIES)
            with c3:
                status = st.selectbox("Status", STATUSES, index=0)

            c4, c5 = st.columns(2)
            with c4:
                due_date = st.date_input("Due Date", value=date.today())
            with c5:
                due_time = st.time_input("Due Time", value=dtime(18, 0))

            submitted = st.form_submit_button("Add Task", use_container_width=True)

            if submitted:
                # ---- Input validation ----
                if not title or not title.strip():
                    st.error("⚠️ Task title cannot be empty.")
                    return

                df = st.session_state.tasks

                # ---- Duplicate prevention ----
                if is_duplicate_task(df, title, category):
                    st.error(f"⚠️ A task titled '{title}' already exists in '{category}'. Please use a different title.")
                    return

                new_row = {
                    "ID": get_next_id(df),
                    "Title": title.strip(),
                    "Description": description.strip(),
                    "Category": category,
                    "Priority": priority,
                    "DueDate": due_date.strftime("%Y-%m-%d"),
                    "DueTime": due_time.strftime("%H:%M:%S"),
                    "Status": status,
                    "CreatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.tasks = df
                save_tasks(df)
                flash("success", f"Task '{title.strip()}' added successfully!")
                st.rerun()


# ----------------------------------------------------------------
# EDIT TASK FORM (inline, shown when a task's Edit button is clicked)
# ----------------------------------------------------------------
def render_edit_task_form(task_row):
    df = st.session_state.tasks
    task_id = int(task_row["ID"])

    st.markdown(f"#### ✏️ Editing: {task_row['Title']}")
    with st.form(f"edit_form_{task_id}"):
        title = st.text_input("Task Title *", value=task_row["Title"])
        description = st.text_area("Task Description", value=task_row["Description"])

        c1, c2, c3 = st.columns(3)
        with c1:
            category = st.selectbox(
                "Category", CATEGORIES,
                index=CATEGORIES.index(task_row["Category"]) if task_row["Category"] in CATEGORIES else 0,
            )
        with c2:
            priority = st.selectbox(
                "Priority Level", PRIORITIES,
                index=PRIORITIES.index(task_row["Priority"]) if task_row["Priority"] in PRIORITIES else 0,
            )
        with c3:
            status = st.selectbox(
                "Status", STATUSES,
                index=STATUSES.index(task_row["Status"]) if task_row["Status"] in STATUSES else 0,
            )

        c4, c5 = st.columns(2)
        with c4:
            try:
                current_date = datetime.strptime(str(task_row["DueDate"]), "%Y-%m-%d").date()
            except Exception:
                current_date = date.today()
            due_date = st.date_input("Due Date", value=current_date)
        with c5:
            try:
                current_time = datetime.strptime(str(task_row["DueTime"]), "%H:%M:%S").time()
            except Exception:
                current_time = dtime(18, 0)
            due_time = st.time_input("Due Time", value=current_time)

        save_col, cancel_col = st.columns(2)
        with save_col:
            save_clicked = st.form_submit_button("💾 Save Changes", use_container_width=True)
        with cancel_col:
            cancel_clicked = st.form_submit_button("✖️ Cancel", use_container_width=True)

        if save_clicked:
            if not title or not title.strip():
                st.error("⚠️ Task title cannot be empty.")
                return
            if is_duplicate_task(df, title, category, exclude_id=task_id):
                st.error(f"⚠️ Another task titled '{title}' already exists in '{category}'.")
                return

            idx = df.index[df["ID"] == task_id][0]
            df.loc[idx, "Title"] = title.strip()
            df.loc[idx, "Description"] = description.strip()
            df.loc[idx, "Category"] = category
            df.loc[idx, "Priority"] = priority
            df.loc[idx, "Status"] = status
            df.loc[idx, "DueDate"] = due_date.strftime("%Y-%m-%d")
            df.loc[idx, "DueTime"] = due_time.strftime("%H:%M:%S")

            st.session_state.tasks = df
            save_tasks(df)
            st.session_state.editing_id = None
            flash("success", f"Task '{title.strip()}' updated successfully!")
            st.rerun()

        if cancel_clicked:
            st.session_state.editing_id = None
            st.rerun()


# ----------------------------------------------------------------
# APPLY FILTERS & SEARCH
# ----------------------------------------------------------------
def apply_filters(df: pd.DataFrame, search_term: str, status_filter: str, category_filter: str) -> pd.DataFrame:
    filtered = df.copy()

    # Status / quick-view filter
    if status_filter == "Completed Tasks":
        filtered = filtered[filtered["Status"] == "Completed"]
    elif status_filter == "Pending Tasks":
        filtered = filtered[filtered["Status"] == "Pending"]
    elif status_filter == "High Priority Tasks":
        filtered = filtered[filtered["Priority"] == "High"]
    # "All Tasks" -> no filtering

    # Category filter
    if category_filter != "All Categories":
        filtered = filtered[filtered["Category"] == category_filter]

    # Search filter (title or description, case-insensitive)
    if search_term and search_term.strip():
        term = search_term.strip().lower()
        filtered = filtered[
            filtered["Title"].astype(str).str.lower().str.contains(term, na=False)
            | filtered["Description"].astype(str).str.lower().str.contains(term, na=False)
        ]

    return filtered


# ----------------------------------------------------------------
# TASK LIST RENDERING
# ----------------------------------------------------------------
def render_task_list(filtered_df: pd.DataFrame):
    if filtered_df.empty:
        st.info("No tasks match the current filters/search. Try adjusting them or add a new task above.")
        return

    # Sort: pending first, then by due date/time ascending
    sortable = filtered_df.copy()
    sortable["_sort_status"] = sortable["Status"].apply(lambda s: 0 if s == "Pending" else 1)
    sortable = sortable.sort_values(by=["_sort_status", "DueDate", "DueTime"])

    for _, row in sortable.iterrows():
        task_id = int(row["ID"])

        # If this task is currently being edited, render the edit form instead of the card
        if st.session_state.editing_id == task_id:
            render_edit_task_form(row)
            st.markdown("---")
            continue

        overdue = is_overdue(row)
        card_class = "completed" if row["Status"] == "Completed" else ("overdue" if overdue else "")

        with st.container():
            st.markdown(f'<div class="task-card {card_class}">', unsafe_allow_html=True)

            top_col, btn_col = st.columns([4, 2])
            with top_col:
                st.markdown(f'<div class="task-title">{row["Title"]}</div>', unsafe_allow_html=True)
                if row["Description"]:
                    st.markdown(f'<div class="task-desc">{row["Description"]}</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="task-meta">'
                    f'{priority_badge(row["Priority"])}'
                    f'<span class="badge badge-cat">{row["Category"]}</span>'
                    f'{status_badge(row["Status"], overdue)}'
                    f' 📅 {row["DueDate"]}  🕒 {row["DueTime"]}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            with btn_col:
                b1, b2, b3 = st.columns(3)
                df = st.session_state.tasks
                idx = df.index[df["ID"] == task_id][0]

                with b1:
                    if row["Status"] == "Pending":
                        if st.button("✅", key=f"complete_{task_id}", help="Mark as Completed", use_container_width=True):
                            df.loc[idx, "Status"] = "Completed"
                            st.session_state.tasks = df
                            save_tasks(df)
                            flash("success", f"Task '{row['Title']}' marked as Completed!")
                            st.rerun()
                    else:
                        if st.button("↩️", key=f"pending_{task_id}", help="Mark as Pending", use_container_width=True):
                            df.loc[idx, "Status"] = "Pending"
                            st.session_state.tasks = df
                            save_tasks(df)
                            flash("success", f"Task '{row['Title']}' marked as Pending!")
                            st.rerun()

                with b2:
                    if st.button("✏️", key=f"edit_{task_id}", help="Edit Task", use_container_width=True):
                        st.session_state.editing_id = task_id
                        st.rerun()

                with b3:
                    if st.button("🗑️", key=f"delete_{task_id}", help="Delete Task", use_container_width=True):
                        df = df[df["ID"] != task_id].reset_index(drop=True)
                        st.session_state.tasks = df
                        save_tasks(df)
                        flash("success", f"Task '{row['Title']}' deleted.")
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------------------
# MAIN APP
# ----------------------------------------------------------------
def main():
    st.markdown(f'<div class="app-title">✅ {APP_TITLE}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Organize your Study, Work, and Personal tasks in one place</div>',
        unsafe_allow_html=True,
    )

    show_flash()

    df = st.session_state.tasks
    search_term, status_filter, category_filter = render_sidebar(df)

    render_dashboard(df)
    render_add_task_form()

    st.subheader("📋 Your Tasks")
    filtered_df = apply_filters(st.session_state.tasks, search_term, status_filter, category_filter)
    render_task_list(filtered_df)


if __name__ == "__main__":
    main()
