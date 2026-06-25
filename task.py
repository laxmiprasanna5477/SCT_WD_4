"""
==========================================================
 Stopwatch Web Application
 Built using Python + Streamlit
==========================================================
Features:
 - Start / Pause / Resume / Reset / Lap buttons
 - Timer displayed in HH:MM:SS:MS format
 - Lap times shown in a table
 - Modern, centered, responsive UI
 - Uses st.session_state to persist stopwatch state across reruns
==========================================================
Run with:
    streamlit run app.py
==========================================================
"""

import time
import streamlit as st
import pandas as pd

# ----------------------------------------------------------------
# PAGE CONFIGURATION
# ----------------------------------------------------------------
st.set_page_config(
    page_title="⏱️ Stopwatch App",
    page_icon="⏱️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ----------------------------------------------------------------
# CUSTOM CSS FOR A MODERN, ATTRACTIVE LOOK
# ----------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Overall app background */
    .stApp {
        background: linear-gradient(135deg, #1f1c2c 0%, #928dab 100%);
    }

    /* Main title styling */
    .title-text {
        text-align: center;
        color: #ffffff;
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: 1px;
        margin-bottom: 0.2rem;
    }

    .subtitle-text {
        text-align: center;
        color: #e0e0e0;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    /* Stopwatch display box */
    .stopwatch-box {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 40px 20px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin-bottom: 25px;
    }

    /* Big timer text */
    .timer-text {
        font-size: 4rem;
        font-weight: 900;
        color: #00ffe0;
        font-family: 'Courier New', monospace;
        letter-spacing: 3px;
        text-shadow: 0 0 15px rgba(0, 255, 224, 0.6);
    }

    /* Status badge */
    .status-running {
        color: #00ff7f;
        font-weight: 700;
        text-align: center;
        font-size: 1rem;
    }
    .status-paused {
        color: #ffcc00;
        font-weight: 700;
        text-align: center;
        font-size: 1rem;
    }
    .status-stopped {
        color: #ff6b6b;
        font-weight: 700;
        text-align: center;
        font-size: 1rem;
    }

    /* Buttons styling */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        font-weight: 700;
        font-size: 1rem;
        border: none;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        transform: scale(1.04);
        box-shadow: 0 0 12px rgba(255,255,255,0.4);
    }

    /* Lap table heading */
    .lap-heading {
        color: #ffffff;
        font-size: 1.3rem;
        font-weight: 700;
        margin-top: 20px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------
# SESSION STATE INITIALIZATION
# ----------------------------------------------------------------
# 'running'    -> True if the stopwatch is currently counting
# 'start_time' -> the reference time.time() when timer was last (re)started
# 'elapsed'    -> total accumulated elapsed seconds (frozen while paused)
# 'laps'       -> list of recorded lap times (strings)
if "running" not in st.session_state:
    st.session_state.running = False
if "start_time" not in st.session_state:
    st.session_state.start_time = 0.0
if "elapsed" not in st.session_state:
    st.session_state.elapsed = 0.0
if "laps" not in st.session_state:
    st.session_state.laps = []
if "message" not in st.session_state:
    st.session_state.message = None  # (type, text) e.g. ("success", "Started!")


# ----------------------------------------------------------------
# HELPER FUNCTION: format seconds -> HH:MM:SS:MS
# ----------------------------------------------------------------
def format_time(total_seconds: float) -> str:
    """Convert a float number of seconds into HH:MM:SS:MS string format."""
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int((total_seconds - int(total_seconds)) * 100)  # 2-digit MS
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{milliseconds:02d}"


def get_current_elapsed() -> float:
    """Return the current total elapsed time, accounting for running state."""
    if st.session_state.running:
        return st.session_state.elapsed + (time.time() - st.session_state.start_time)
    return st.session_state.elapsed


# ----------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------
st.markdown('<div class="title-text">⏱️ Stopwatch</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle-text">A modern stopwatch with Start, Pause, Resume, Reset & Lap</div>',
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------
# STOPWATCH DISPLAY
# ----------------------------------------------------------------
current_elapsed = get_current_elapsed()
display_time = format_time(current_elapsed)

timer_placeholder = st.empty()
with timer_placeholder.container():
    st.markdown(
        f"""
        <div class="stopwatch-box">
            <div class="timer-text">{display_time}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Status indicator
if st.session_state.running:
    st.markdown('<div class="status-running">● RUNNING</div>', unsafe_allow_html=True)
elif current_elapsed > 0:
    st.markdown('<div class="status-paused">⏸ PAUSED</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-stopped">■ STOPPED</div>', unsafe_allow_html=True)

# Show any pending message (success/info) from the last button action
if st.session_state.message:
    msg_type, msg_text = st.session_state.message
    if msg_type == "success":
        st.success(msg_text)
    elif msg_type == "info":
        st.info(msg_text)
    elif msg_type == "warning":
        st.warning(msg_text)
    st.session_state.message = None  # clear after showing once

st.write("")  # spacing

# ----------------------------------------------------------------
# CONTROL BUTTONS (Start, Pause, Resume, Reset, Lap)
# ----------------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    start_clicked = st.button("▶️ Start", use_container_width=True)

with col2:
    pause_clicked = st.button("⏸️ Pause", use_container_width=True)

with col3:
    resume_clicked = st.button("⏯️ Resume", use_container_width=True)

with col4:
    reset_clicked = st.button("🔄 Reset", use_container_width=True)

with col5:
    lap_clicked = st.button("🚩 Lap", use_container_width=True)

# ----------------------------------------------------------------
# BUTTON LOGIC
# ----------------------------------------------------------------

# START: begin counting from zero (or continue if already has elapsed time)
if start_clicked:
    if not st.session_state.running:
        st.session_state.start_time = time.time() - st.session_state.elapsed
        st.session_state.running = True
        st.session_state.message = ("success", "Stopwatch started!")
    else:
        st.session_state.message = ("info", "Stopwatch is already running.")

# PAUSE: freeze the elapsed time
if pause_clicked:
    if st.session_state.running:
        st.session_state.elapsed = time.time() - st.session_state.start_time
        st.session_state.running = False
        st.session_state.message = ("info", "Stopwatch paused.")
    else:
        st.session_state.message = ("warning", "Stopwatch is not running, nothing to pause.")

# RESUME: continue counting from where it was paused
if resume_clicked:
    if not st.session_state.running and st.session_state.elapsed > 0:
        st.session_state.start_time = time.time() - st.session_state.elapsed
        st.session_state.running = True
        st.session_state.message = ("success", "Stopwatch resumed!")
    elif st.session_state.running:
        st.session_state.message = ("info", "Stopwatch is already running.")
    else:
        st.session_state.message = ("warning", "Nothing to resume. Click Start first.")

# RESET: clear everything back to zero
if reset_clicked:
    st.session_state.running = False
    st.session_state.start_time = 0.0
    st.session_state.elapsed = 0.0
    st.session_state.laps = []
    st.session_state.message = ("success", "Stopwatch reset successfully!")

# LAP: record the current elapsed time, but only if the timer has actually started
if lap_clicked:
    if not st.session_state.running and st.session_state.elapsed == 0:
        # Prevent errors when Lap is clicked before Start
        st.session_state.message = ("warning", "Please start the stopwatch before recording a lap.")
    else:
        lap_time = get_current_elapsed()
        lap_number = len(st.session_state.laps) + 1
        st.session_state.laps.append(
            {"Lap": lap_number, "Lap Time": format_time(lap_time)}
        )
        st.session_state.message = ("success", f"Lap {lap_number} recorded at {format_time(lap_time)}!")

# ----------------------------------------------------------------
# TOTAL ELAPSED TIME SUMMARY
# ----------------------------------------------------------------
st.write("")
st.markdown(
    f"<p style='text-align:center; color:#dddddd; font-size:1rem;'>"
    f"<b>Total Elapsed Time:</b> {format_time(get_current_elapsed())}</p>",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------
# LAP TIMES TABLE
# ----------------------------------------------------------------
st.markdown('<div class="lap-heading">🚩 Lap Times</div>', unsafe_allow_html=True)

if st.session_state.laps:
    laps_df = pd.DataFrame(st.session_state.laps)
    st.dataframe(laps_df, use_container_width=True, hide_index=True)
else:
    st.info("No laps recorded yet. Click 'Lap' while the stopwatch is running to record one.")

# ----------------------------------------------------------------
# AUTO-REFRESH LOGIC
# ----------------------------------------------------------------
# Streamlit reruns the whole script on each interaction. To make the
# timer appear "live" while running, we pause briefly and trigger a
# rerun. This keeps the displayed time updating continuously and still
# allows button clicks (Pause/Reset/Lap) to be captured on each rerun.
if st.session_state.running:
    time.sleep(0.05)
    st.rerun()
