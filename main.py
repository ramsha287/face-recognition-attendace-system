from fastapi import FastAPI, File, UploadFile, Form
import cv2
import numpy as np
import os
import csv
from datetime import datetime
import threading
import torch
import mediapipe as mp

# Face embeddings (no dlib)
from facenet_pytorch import InceptionResnetV1

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STUDENT_IMAGES_DIR = "faces"
ATTENDANCE_FILE = "attendance.csv"

os.makedirs(STUDENT_IMAGES_DIR, exist_ok=True)

known_embeddings = []
known_names = []
attendance_running = False

# 🔥 MediaPipe detector
mp_face = mp.solutions.face_detection
detector = mp_face.FaceDetection(model_selection=1, min_detection_confidence=0.5)

# 🔥 FaceNet model (embeddings)
embedder = InceptionResnetV1(pretrained='vggface2').eval()


# --------------------------
# 🧠 UTIL FUNCTIONS
# --------------------------

def get_embedding(face_img):
    face_img = cv2.resize(face_img, (160, 160))
    face_img = face_img.astype(np.float32) / 255.0
    face_img = np.transpose(face_img, (2, 0, 1))
    face_img = np.expand_dims(face_img, axis=0)

    tensor = torch.tensor(face_img)
    with torch.no_grad():
        emb = embedder(tensor).numpy()[0]
    return emb


def extract_face(image):
    if image is None:
        return None

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = detector.process(rgb)
    if not results.detections:
        return None

    bbox = results.detections[0].location_data.relative_bounding_box
    h, w, _ = image.shape

    x1 = max(0, int(bbox.xmin * w))
    y1 = max(0, int(bbox.ymin * h))
    x2 = min(w, int((bbox.xmin + bbox.width) * w))
    y2 = min(h, int((bbox.ymin + bbox.height) * h))

    if x2 <= x1 or y2 <= y1:
        return None

    face = image[y1:y2, x1:x2]
    if face.size == 0:
        return None

    return face


def ensure_attendance_file():
    if not os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Time", "Date"])


def load_known_faces():
    global known_embeddings, known_names
    known_embeddings = []
    known_names = []

    for file in os.listdir(STUDENT_IMAGES_DIR):
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            path = os.path.join(STUDENT_IMAGES_DIR, file)
            image = cv2.imread(path)

            if image is None:
                print(f"⚠️ Could not read {file}")
                continue

            face = extract_face(image)
            if face is None:
                print(f"⚠️ No face in {file}")
                continue

            emb = get_embedding(face)
            known_embeddings.append(emb)
            known_names.append(os.path.splitext(file)[0])


ensure_attendance_file()
load_known_faces()


def compare_embeddings(emb1, emb2):
    return np.linalg.norm(emb1 - emb2)


# --------------------------
# 📥 ENROLL
# --------------------------

@app.post("/enroll/")
async def enroll(name: str = Form(...), file: UploadFile = File(...)):
    try:
        if name in known_names:
            return {"error": f"Student '{name}' already enrolled"}

        contents = await file.read()
        file_path = os.path.join(STUDENT_IMAGES_DIR, f"{name}.jpg")

        with open(file_path, "wb") as f:
            f.write(contents)

        image = cv2.imread(file_path)
        if image is None:
            os.remove(file_path)
            return {"error": "Invalid image format"}

        face = extract_face(image)
        if face is None:
            os.remove(file_path)
            return {"error": "No face detected"}

        emb = get_embedding(face)

        known_embeddings.append(emb)
        known_names.append(name)

        return {"message": f"{name} enrolled successfully"}

    except Exception as e:
        return {"error": str(e)}


# --------------------------
# 🎥 ATTENDANCE
# --------------------------

def mark_attendance():
    global attendance_running

    cam = cv2.VideoCapture(0)
    marked = set()

    while attendance_running:
        ret, frame = cam.read()
        if not ret:
            break

        face = extract_face(frame)

        if face is not None and len(known_embeddings) > 0:
            emb = get_embedding(face)

            distances = [compare_embeddings(emb, k) for k in known_embeddings]
            idx = int(np.argmin(distances))

            if distances[idx] < 0.8:
                name = known_names[idx]

                if name not in marked:
                    now = datetime.now()
                    time = now.strftime("%H:%M:%S")
                    date = now.strftime("%Y-%m-%d")

                    with open(ATTENDANCE_FILE, "a", newline="") as f:
                        csv.writer(f).writerow([name, time, date])

                    try:
                        from automation.sheets import mark_attendance as sheet_mark
                        sheet_mark(name, time, date)
                    except Exception as e:
                        print(f"⚠️ Google sheet logging failed: {e}")

                    marked.add(name)
                    print(f"✅ {name} marked")

                cv2.putText(frame, name, (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        cv2.imshow("Attendance", frame)

        if cv2.waitKey(1) == 27:
            break

    cam.release()
    cv2.destroyAllWindows()


# --------------------------
# 🚀 START / STOP
# --------------------------

@app.get("/start-attendance/")
async def start():
    global attendance_running

    if attendance_running:
        return {"message": "Already running"}

    if not known_embeddings:
        return {"message": "No students enrolled"}

    attendance_running = True
    threading.Thread(target=mark_attendance, daemon=True).start()

    return {"message": "Attendance started"}


@app.get("/status/")
async def status():
    return {
        "attendance_running": attendance_running,
        "registered_students": len(known_names),
        "students": known_names,
    }


@app.get("/stop-attendance/")
async def stop():
    global attendance_running
    attendance_running = False
    return {"message": "Stopped"}


@app.get("/students/")
async def students():
    return {"students": known_names}