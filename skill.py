import streamlit as st

st.title("🎯 Quiz Game")

# Initialize level
if "level" not in st.session_state:
    st.session_state.level = 1

# Level 1 Questions
level1 = [
    {"question": "What is the capital of India?",
     "options": ["Mumbai", "Delhi", "Chennai", "Kolkata"],
     "answer": "Delhi"},

    {"question": "Which language is used for Streamlit?",
     "options": ["Java", "Python", "C++", "PHP"],
     "answer": "Python"},

    {"question": "Who is known as the Father of the Nation in India?",
     "options": ["Nehru", "Gandhi", "Patel", "Bose"],
     "answer": "Gandhi"},

    {"question": "How many days are there in a week?",
     "options": ["5", "6", "7", "8"],
     "answer": "7"},

    {"question": "What is 5 + 3?",
     "options": ["6", "7", "8", "9"],
     "answer": "8"}
]

# Level 2 Questions
level2 = [
    {"question": "Which planet is known as the Red Planet?",
     "options": ["Earth", "Mars", "Jupiter", "Venus"],
     "answer": "Mars"},

    {"question": "Who developed Python?",
     "options": ["Dennis Ritchie", "Guido van Rossum", "James Gosling", "Bjarne Stroustrup"],
     "answer": "Guido van Rossum"},

    {"question": "Which keyword is used to define a function in Python?",
     "options": ["func", "define", "def", "function"],
     "answer": "def"},

    {"question": "Which is the largest ocean?",
     "options": ["Atlantic", "Indian", "Pacific", "Arctic"],
     "answer": "Pacific"},

    {"question": "What is the square root of 64?",
     "options": ["6", "7", "8", "9"],
     "answer": "8"}
]

questions = level1 if st.session_state.level == 1 else level2

st.subheader(f"Level {st.session_state.level}")

# Display questions
for i, q in enumerate(questions):
    st.radio(
        q["question"],
        q["options"],
        key=f"q_{st.session_state.level}_{i}"
    )

# Submit button
if st.button("Submit Quiz"):
    score = 0

    for i, q in enumerate(questions):
        if st.session_state[f"q_{st.session_state.level}_{i}"] == q["answer"]:
            score += 1

    st.success(f"Your Score: {score}/{len(questions)}")

    # Level 1 completed
    if st.session_state.level == 1:
        if score >= 3:
            st.session_state.level = 2
            st.success("🎉 Congratulations! Level 2 Unlocked!")
            st.rerun()
        else:
            st.error("❌ Score at least 3/5 to unlock Level 2.")

    # Level 2 completed
    else:
        st.balloons()
        st.success("🏆 Quiz Completed Successfully!")
        