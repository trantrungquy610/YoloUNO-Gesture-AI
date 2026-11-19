"""Crop/resize webcam frames to 64x64 grayscale and POST raw bytes to YOLO UNO.
The laptop does not run inference; CNN inference belongs on the ESP32-S3.
"""
import argparse
import time
import cv2
import requests

SIZE = 64

def preprocess(frame):
    frame = cv2.flip(frame, 1)
    h, w = frame.shape[:2]
    side = min(h, w) * 3 // 4
    x, y = (w - side) // 2, (h - side) // 2
    crop = frame[y:y + side, x:x + side]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(gray, (SIZE, SIZE), interpolation=cv2.INTER_AREA)
    return small

parser = argparse.ArgumentParser()
parser.add_argument("--url", required=True, help="e.g. http://192.168.1.80:8080/api/gesture/frame")
parser.add_argument("--camera", type=int, default=0)
parser.add_argument("--fps", type=float, default=2.0, help="Start conservatively at 2 FPS")
parser.add_argument("--preview", action="store_true")
args = parser.parse_args()

cap = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)
if not cap.isOpened():
    cap = cv2.VideoCapture(args.camera)
if not cap.isOpened():
    raise SystemExit("Cannot open webcam")

period = 1.0 / max(0.2, min(args.fps, 10.0))
session = requests.Session()
print(f"Sending 4096-byte frames to {args.url}; Ctrl+C to stop")
try:
    while True:
        started = time.monotonic()
        ok, frame = cap.read()
        if not ok:
            continue
        image = preprocess(frame)
        try:
            response = session.post(
                args.url,
                data=image.tobytes(),
                headers={"Content-Type": "application/octet-stream"},
                timeout=3,
            )
            print(f"HTTP {response.status_code}: {response.text[:160]}")
        except requests.RequestException as exc:
            print(f"POST failed: {exc}")

        if args.preview:
            cv2.imshow("Frame sent to YOLO UNO (64x64 grayscale)", image)
            if cv2.waitKey(1) & 0xFF in (ord("q"), ord("Q")):
                break
        time.sleep(max(0, period - (time.monotonic() - started)))
except KeyboardInterrupt:
    print("Stopped")
finally:
    cap.release()
    cv2.destroyAllWindows()
    session.close()
