import cv2

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Camera open nahi hua!")
    raise SystemExit

print("Camera start ho gaya. Band karne ke liye Q dabao.")

while True:
    success, frame = camera.read()

    if not success:
        print("Camera frame read nahi hua!")
        break

    cv2.imshow("Smart Attendance - Camera Test", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()