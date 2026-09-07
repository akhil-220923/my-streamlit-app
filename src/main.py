from ultralytics import YOLO
import cv2

# Load YOLO model
model = YOLO("../models/yolo11s.pt")

# Open input video
cap = cv2.VideoCapture("../data/video.mp4")

while True:
    success, frame = cap.read()

    if not success:
        break

    # Detect + track objects
    results = model.track(
        frame,
        persist=True,
        classes=[0]  # 0 = person
    )

    # Draw detections
    annotated_frame = results[0].plot()

    # Display
    cv2.imshow("AI Border Surveillance", annotated_frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()