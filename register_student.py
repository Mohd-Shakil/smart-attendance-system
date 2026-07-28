import csv
import os
import re
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "student_images"
)

CSV_FILE = os.path.join(
    BASE_DIR,
    "database",
    "students.csv"
)

DB_FILE = os.path.join(
    BASE_DIR,
    "database",
    "attendance.db"
)


def register_student():
    print("\n===== Student Registration =====")

    student_id = input("Enter Student ID: ").strip()
    student_name = input("Enter Student Name: ").strip()

    if not student_id or not student_name:
        print("ID aur Name empty nahi ho sakte!")
        return

    if not student_id.isalnum():
        print("Student ID mein sirf letters aur numbers use karo!")
        return

    safe_name = re.sub(
        r'[<>:"/\\|?*]',
        "",
        student_name
    ).strip()

    folder_name = (
        f"{student_id}_{safe_name.replace(' ', '_')}"
    )

    student_folder = os.path.join(
        DATASET_PATH,
        folder_name
    )

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT student_id FROM students WHERE student_id = ?",
        (student_id,)
    )

    if cursor.fetchone():
        print(f"Student ID {student_id} pehle se registered hai!")
        connection.close()
        return

    cursor.execute("""
        INSERT INTO students (
            student_id,
            student_name,
            image_folder
        )
        VALUES (?, ?, ?)
    """, (
        student_id,
        student_name,
        folder_name
    ))

    connection.commit()
    connection.close()

    os.makedirs(student_folder, exist_ok=True)

    file_is_empty = (
        not os.path.exists(CSV_FILE)
        or os.path.getsize(CSV_FILE) == 0
    )

    with open(
        CSV_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        if file_is_empty:
            writer.writerow([
                "student_id",
                "student_name",
                "image_folder"
            ])

        writer.writerow([
            student_id,
            student_name,
            folder_name
        ])

    print("\nStudent successfully registered!")
    print(f"Student ID: {student_id}")
    print(f"Student Name: {student_name}")
    print(f"Folder created: {student_folder}")
    print("Student CSV aur database dono mein saved hai.")


if __name__ == "__main__":
    register_student()