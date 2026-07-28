import json
import os

import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "student_images"
)

MODELS_PATH = os.path.join(
    BASE_DIR,
    "models"
)

MODEL_FILE = os.path.join(
    MODELS_PATH,
    "face_model.yml"
)

LABEL_FILE = os.path.join(
    MODELS_PATH,
    "labels.json"
)


def train_model():
    print("\n===== Face Model Training =====")

    os.makedirs(MODELS_PATH, exist_ok=True)

    if not os.path.exists(DATASET_PATH):
        print("Student images ka folder nahi mila!")
        return

    face_images = []
    face_labels = []
    label_map = {}

    current_label = 0

    student_folders = sorted(os.listdir(DATASET_PATH))

    for folder_name in student_folders:
        student_folder = os.path.join(
            DATASET_PATH,
            folder_name
        )

        if not os.path.isdir(student_folder):
            continue

        current_label += 1
        label_map[current_label] = folder_name

        image_count = 0

        for image_name in os.listdir(student_folder):
            if not image_name.lower().endswith(
                (".jpg", ".jpeg", ".png")
            ):
                continue

            image_path = os.path.join(
                student_folder,
                image_name
            )

            image = cv2.imread(
                image_path,
                cv2.IMREAD_GRAYSCALE
            )

            if image is None:
                print(f"Image read nahi hui: {image_name}")
                continue

            image = cv2.resize(image, (200, 200))

            face_images.append(image)
            face_labels.append(current_label)
            image_count += 1

        print(
            f"{folder_name}: {image_count} images loaded"
        )

    if len(face_images) == 0:
        print("Training ke liye koi image nahi mili!")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()

    recognizer.train(
        face_images,
        np.array(face_labels)
    )

    recognizer.write(MODEL_FILE)

    with open(
        LABEL_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            label_map,
            file,
            indent=4
        )

    print("\nModel training successfully complete!")
    print(f"Total images trained: {len(face_images)}")
    print(f"Model saved: {MODEL_FILE}")
    print(f"Labels saved: {LABEL_FILE}")


if __name__ == "__main__":
    train_model()