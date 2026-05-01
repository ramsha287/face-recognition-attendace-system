import streamlit as st
import pandas as pd
import requests
import time

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Attendance System", layout="wide")

st.title("🎓 Face Recognition Attendance Dashboard")

# --------------------------
# 🚀 CONTROL PANEL
# --------------------------
st.subheader("🎮 Control Panel")

col1, col2 = st.columns(2)

if col1.button("▶ Start Attendance"):
    res = requests.get(f"{API_URL}/start-attendance/")
    st.success(res.json()["message"])

if col2.button("⏹ Stop Attendance"):
    res = requests.get(f"{API_URL}/stop-attendance/")
    st.warning(res.json()["message"])


# --------------------------
# 👤 ENROLL STUDENT
# --------------------------
st.subheader("👤 Enroll New Student")

name = st.text_input("Enter Student Name")
image = st.file_uploader("Upload Face Image", type=["jpg", "jpeg", "png"])

if st.button("Enroll"):
    if name and image:
        files = {"file": image}
        data = {"name": name}

        res = requests.post(f"{API_URL}/enroll/", files=files, data=data)

        st.success(res.json())
    else:
        st.error("Please enter name and upload image")


# --------------------------
# 📊 STUDENTS LIST
# --------------------------
st.subheader("📋 Registered Students")

try:
    res = requests.get(f"{API_URL}/students/")
    students = res.json().get("students", [])

    if students:
        st.write(students)
    else:
        st.info("No students enrolled yet.")

except:
    st.error("Backend not running")


# --------------------------
# 📈 ATTENDANCE DATA
# --------------------------
st.subheader("📊 Attendance Records")

try:
    df = pd.read_csv("attendance.csv")

    st.dataframe(df)

    st.subheader("📈 Attendance Count")
    st.bar_chart(df["Name"].value_counts())

except:
    st.info("No attendance data yet.")


# --------------------------
# 🔄 AUTO REFRESH
# --------------------------
st.subheader("🔄 Live Refresh")

if st.checkbox("Auto Refresh (every 5 sec)"):
    time.sleep(5)
    st.rerun()