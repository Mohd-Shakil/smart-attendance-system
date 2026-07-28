import csv
import json
import os
import sqlite3
from datetime import datetime

import cv2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_FILE = os.path.join(
    BASE_DIR,
    "database",
    "attendance.db"
)

MODEL_FILE = os.path.join(
    BASE_DIR,
    "models",
    "face_model.yml"
)

LABEL_FILE = os.path.join(
    BASE_DIR,
    "models",
    "labels.json"
)

ATTENDANCE_FILE = os.path.join(
    BASE_DIR,
    "attendance",
    "attendance.csv"
)


def save_attendance(student_id, student_name):
    os.makedirs(
        os.path.dirname(ATTENDANCE_FILE),
        exist_ok=True
    )

    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT attendance_id
        FROM attendance
        WHERE student_id = ? AND date = ?
    """, (
        student_id,
        today
    ))

    if cursor.fetchone():
        connection.close()
        return False

    cursor.execute("""
        INSERT INTO attendance (
            student_id,
            student_name,
            date,
            time,
            status
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        student_id,
        student_name,
        today,
        current_time,
        "Present"
    ))

    connection.commit()
    connection.close()

    file_is_empty = (
        not os.path.exists(ATTENDANCE_FILE)
        or os.path.getsize(ATTENDANCE_FILE) == 0
    )

    with open(
        ATTENDANCE_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        if file_is_empty:
            writer.writerow([
                "student_id",
                "student_name",
                "date",
                "time",
                "status"
            ])

        writer.writerow([
            student_id,
            student_name,
            today,
            current_time,
            "Present"
        ])

    print(f"Attendance marked: {student_name}")
    print("Attendance CSV aur database dono mein saved hai.")

    return True


def start_recognition():
    print("\n===== Smart Attendance System =====")

    if not os.path.exists(MODEL_FILE):
        print("Face model nahi mila! Pehle train_model.py run karo.")
        return

    if not os.path.exists(LABEL_FILE):
        print("Labels file nahi mili!")
        return

    with open(LABEL_FILE, "r", encoding="utf-8") as file:
        labels = json.load(file)

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_FILE)

    face_detector = cv2.CascadeClassifier(
        cv2.data.haarcascades
        + "haarcascade_frontalface_default.xml"
    )

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Camera open nahi hua!")
        return

    recognition_counts = {}

    print("Camera start ho gaya.")
    print("Band karne ke liye Q dabao.")

    while True:
        success, frame = camera.read()

        if not success:
            print("Camera frame read nahi hua!")
            break

        gray_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = face_detector.detectMultiScale(
            gray_frame,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(100, 100)
        )

        for x, y, width, height in faces:
            face_image = gray_frame[
                y:y + height,
                x:x + width
            ]

            face_image = cv2.resize(
                face_image,
                (200, 200)
            )

            label, distance = recognizer.predict(face_image)

            # LBPH mein kam distance better match hota hai
            if distance < 65 and str(label) in labels:
                folder_name = labels[str(label)]

                parts = folder_name.split("_", 1)
                student_id = parts[0]

                if len(parts) > 1:
                    student_name = parts[1].replace("_", " ")
                else:
                    student_name = folder_name

                recognition_counts[student_id] = (
                    recognition_counts.get(student_id, 0) + 1
                )

                name_to_show = student_name
                color = (0, 255, 0)

                # Lagatar multiple recognition ke baad attendance
                if recognition_counts[student_id] == 8:
                    save_attendance(
                        student_id,
                        student_name
                    )

                match_score = max(
                    0,
                    min(100, round(100 - distance))
                )

                text = f"{name_to_show} - Match: {match_score}%"

            else:
                text = "Unknown Person"
                color = (0, 0, 255)

            cv2.rectangle(
                frame,
                (x, y),
                (x + width, y + height),
                color,
                2
            )

            cv2.putText(
                frame,
                text,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2
            )

        cv2.imshow(
            "Smart Attendance System",
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    start_recognition()