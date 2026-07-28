import csv
import os
import cv2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_FILE = os.path.join(
    BASE_DIR,
    "database",
    "students.csv"
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "student_images"
)


def find_student(student_id):
    if not os.path.exists(CSV_FILE):
        return None

    with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["student_id"] == student_id:
                return row

    return None


def capture_faces():
    print("\n===== Face Image Capture =====")

    student_id = input("Enter registered Student ID: ").strip()
    student = find_student(student_id)

    if student is None:
        print("Student ID registered nahi hai!")
        return

    student_name = student["student_name"]
    folder_name = student["image_folder"]
    student_folder = os.path.join(DATASET_PATH, folder_name)

    os.makedirs(student_folder, exist_ok=True)

    face_detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Camera open nahi hua!")
        return

    image_count = 0
    maximum_images = 30

    print(f"\nStudent: {student_name}")
    print("Camera ki taraf dekho aur chehra thoda move karo.")
    print("Program band karne ke liye Q dabao.")

    while image_count < maximum_images:
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

            image_count += 1

            image_path = os.path.join(
                student_folder,
                f"{student_id}_{image_count}.jpg"
            )

            cv2.imwrite(image_path, face_image)

            cv2.rectangle(
                frame,
                (x, y),
                (x + width, y + height),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Images: {image_count}/{maximum_images}",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

        cv2.imshow("Face Image Capture", frame)

        if cv2.waitKey(100) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()

    print(f"\n{image_count} face images successfully saved!")
    print(f"Location: {student_folder}")


if __name__ == "__main__":
    capture_faces()