import streamlit as st
import re
import random
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import threading

# Initialize FastAPI app
app = FastAPI()

# Blacklist of common passwords
BLACKLISTED_PASSWORDS = {"password", "123456", "12345678", "qwerty", "abc123", "password123"}

# Custom password scoring weights
WEIGHTS = {
    "length": 2,  
    "uppercase_lowercase": 1,
    "digit": 1,
    "special_char": 1
}

class PasswordInput(BaseModel):
    password: str

def check_password_strength(password: str):
    score = 0
    feedback = []

    # Blacklist Check
    if password.lower() in BLACKLISTED_PASSWORDS:
        return 0, ["❌ This password is too common. Please choose a more secure one."]

    # Length Check
    if len(password) >= 8:
        score += WEIGHTS["length"]
    else:
        feedback.append("❌ Password should be at least 8 characters long.")

    # Upper & Lowercase Check
    if re.search(r"[A-Z]", password) and re.search(r"[a-z]", password):
        score += WEIGHTS["uppercase_lowercase"]
    else:
        feedback.append("❌ Include both uppercase and lowercase letters.")

    # Digit Check
    if re.search(r"\d", password):
        score += WEIGHTS["digit"]
    else:
        feedback.append("❌ Add at least one number (0-9).")

    # Special Character Check
    if re.search(r"[!@#$%^&*]", password):
        score += WEIGHTS["special_char"]
    else:
        feedback.append("❌ Include at least one special character (!@#$%^&*).")

    return score, feedback

def generate_strong_password():
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    return "".join(random.choice(characters) for _ in range(12))

@app.post("/check-password")
def api_check_password(data: PasswordInput):
    score, feedback = check_password_strength(data.password)
    return {"score": score, "feedback": feedback}

def run_fastapi():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

# Run FastAPI in a separate thread
threading.Thread(target=run_fastapi, daemon=True).start()

# Streamlit UI
st.title("🔐 Advanced Password Strength Meter")
st.write("Check your password security and get improvement suggestions!")

# User Input
password = st.text_input("Enter your password:", type="password")

if password:
    score, feedback = check_password_strength(password)

    # Strength Indicator (Color-Coded)
    if score >= 5:
        st.success("✅ Strong Password!")
        st.progress(100)
        bar_color = "green"
    elif score >= 3:
        st.warning("⚠️ Moderate Password - Consider adding more security features.")
        st.progress(75)
        bar_color = "orange"
    else:
        st.error("❌ Weak Password - Improve it using the suggestions below.")
        st.progress(50)
        bar_color = "red"

    # Show Feedback
    if feedback:
        for item in feedback:
            st.write(item)
    
    # Suggest a Strong Password
    st.write("🔹 Need a strong password? Try this:")
    st.code(generate_strong_password())
