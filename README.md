# Agentic AI Workflow for Attendance Automation using Face Recognition

A full-stack AI-powered attendance system that uses **face recognition** to automate student attendance marking. Built with **FastAPI**, **Streamlit**, and **MediaPipe + FaceNet**, and integrated with **Google Sheets** for real-time logging.

---

## Features

* 👤 **Face Enrollment API** – Register new students using image upload
* 🎥 **Real-time Attendance** – Detect and recognize faces via webcam
* 🧠 **AI-Based Recognition** – Uses FaceNet embeddings for accurate matching
* 📊 **Streamlit Dashboard** – Interactive UI for monitoring attendance
* ☁️ **Google Sheets Integration** – Automatically logs attendance data
* 📁 **CSV Logging** – Local backup of attendance records
* 🔄 **Auto Refresh Dashboard** – Real-time updates

---

## 🛠️ Tech Stack

* **Backend:** FastAPI
* **Frontend:** Streamlit
* **Face Detection:** MediaPipe
* **Face Recognition:** FaceNet (facenet-pytorch)
* **Computer Vision:** OpenCV
* **Data Handling:** Pandas
* **Cloud Integration:** Google Sheets API (gspread)

---

## Project Structure

```
face-recognition-attendance-system/
│── main.py                 # FastAPI backend
│── dashboard.py           # Streamlit UI
│── requirements.txt       # Dependencies
│── README.md              # Project documentation
│── automation/
│    └── sheets.py         # Google Sheets integration
│── faces/                 # Stored student images (ignored in git)
│── attendance.csv         # Local attendance logs
```

---

## Installation

### Clone the repository

```bash
git clone https://github.com/ramsha287/face-recognition-attendace-system.git
cd face-recognition-attendace-system
```

---

### Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

---

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Application

### Start FastAPI backend

```bash
uvicorn main:app --reload
```

---

### Start Streamlit dashboard

```bash
streamlit run dashboard.py
```

---

## API Endpoints

| Method | Endpoint             | Description              |
| ------ | -------------------- | ------------------------ |
| POST   | `/enroll/`           | Enroll new student       |
| GET    | `/start-attendance/` | Start attendance system  |
| GET    | `/stop-attendance/`  | Stop attendance          |
| GET    | `/students/`         | List registered students |
| GET    | `/status/`           | System status            |

---

## Dashboard Features

* Start/Stop attendance
* Enroll students via UI
* View registered students
* Display attendance logs
* Visualize attendance analytics

---

## Google Sheets Setup

1. Create a Google Cloud project
2. Enable Google Sheets API
3. Create a Service Account
4. Download `credentials.json`
5. Share your Google Sheet with the service account email

---

## Demo

<img width="1913" height="831" alt="image" src="https://github.com/user-attachments/assets/7304f8cc-988b-40d5-8821-78865a1bce2b" />


---

## Future Improvements

* Authentication system (admin login)
* Deployment (AWS / Render / Docker)
* Mobile-friendly UI
* Multi-face tracking
* Advanced analytics dashboard


