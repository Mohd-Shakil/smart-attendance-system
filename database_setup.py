import csv
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_FILE = os.path.join(
    BASE_DIR,
    "database",
    "attendance.db"
)

STUDENTS_CSV = os.path.join(
    BASE_DIR,
    "database",
    "students.csv"
)

ATTENDANCE_CSV = os.path.join(
    BASE_DIR,
    "attendance",
    "attendance.csv"
)


def create_database():
    os.makedirs(
        os.path.dirname(DB_FILE),
        exist_ok=True
    )

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            student_name TEXT NOT NULL,
            image_folder TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            student_name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT DEFAULT 'Present',
            UNIQUE(student_id, date)
        )
    """)

    # Existing students.csv ko database mein import karo
    if os.path.exists(STUDENTS_CSV):
        with open(
            STUDENTS_CSV,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                cursor.execute("""
                    INSERT OR IGNORE INTO students (
                        student_id,
                        student_name,
                        image_folder
                    )
                    VALUES (?, ?, ?)
                """, (
                    row.get("student_id", ""),
                    row.get("student_name", ""),
                    row.get("image_folder", "")
                ))

    # Existing attendance.csv ko database mein import karo
    if os.path.exists(ATTENDANCE_CSV):
        with open(
            ATTENDANCE_CSV,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                cursor.execute("""
                    INSERT OR IGNORE INTO attendance (
                        student_id,
                        student_name,
                        date,
                        time,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    row.get("student_id", ""),
                    row.get("student_name", ""),
                    row.get("date", ""),
                    row.get("time", ""),
                    row.get("status", "Present")
                ))

    connection.commit()

    cursor.execute("SELECT COUNT(*) FROM students")
    student_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attendance")
    attendance_count = cursor.fetchone()[0]

    connection.close()

    print("\nDatabase successfully updated!")
    print(f"Total students: {student_count}")
    print(f"Attendance records: {attendance_count}")


if __name__ == "__main__":
    create_database()