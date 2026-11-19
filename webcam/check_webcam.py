"""Show the webcam's current capture resolution and live preview."""
import cv2

CAMERA_INDEX = 0

cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)  # Windows; remove CAP_DSHOW if needed
if not cap.isOpened():
    cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    raise SystemExit("Cannot open webcam. Close apps using the camera or try CAMERA_INDEX=1.")

# Ask for a common mode; the driver may choose a different supported mode.
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

ok, frame = cap.read()
if not ok:
    cap.release()
    raise SystemExit("Webcam opened but no frame could be read.")

h, w = frame.shape[:2]
fps = cap.get(cv2.CAP_PROP_FPS)
print(f"Actual capture resolution: {w} x {h}")
print(f"Driver-reported FPS: {fps:.1f}")
print("Press Q to close the preview.")

while True:
    ok, frame = cap.read()
    if not ok:
        break
    h, w = frame.shape[:2]
    cv2.putText(frame, f"{w}x{h} | Q: quit", (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.imshow("YOLO UNO webcam check", frame)
    if cv2.waitKey(1) & 0xFF in (ord("q"), ord("Q")):
        break

cap.release()
cv2.destroyAllWindows()
