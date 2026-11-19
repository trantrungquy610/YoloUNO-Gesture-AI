"""Collect grayscale 64x64 gesture crops from a webcam.

Keys 1..5 select a class; SPACE saves one image; Q exits.
Each run creates a separate session folder so sessions can later be split
between train/validation/test without leaking near-duplicate frames.
"""
from datetime import datetime
from pathlib import Path
import cv2

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "dataset" / "raw"
SIZE = 64
CAMERA_INDEX = 0
CLASSES = {
    ord("1"): "open_palm",
    ord("2"): "fist",
    ord("3"): "thumbs_up",
    ord("4"): "victory",
    ord("5"): "no_hand",
}
SESSION = datetime.now().strftime("%Y%m%d_%H%M%S")

cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
if not cap.isOpened():
    cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    raise SystemExit("Cannot open webcam. Try CAMERA_INDEX=1 or close other camera apps.")

selected = None
saved = 0
print("1 Open Palm | 2 Fist | 3 Thumbs Up | 4 Victory | 5 No Hand")
print("SPACE = save image; Q = quit. Move/rotate hand and vary lighting/background.")

while True:
    ok, frame = cap.read()
    if not ok:
        print("Frame read failed")
        break
    frame = cv2.flip(frame, 1)
    h, w = frame.shape[:2]
    side = min(h, w) * 3 // 4
    x, y = (w - side) // 2, (h - side) // 2
    crop = frame[y:y + side, x:x + side]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    sample = cv2.resize(gray, (SIZE, SIZE), interpolation=cv2.INTER_AREA)

    shown = frame.copy()
    cv2.rectangle(shown, (x, y), (x + side, y + side), (0, 255, 0), 2)
    cv2.putText(shown, f"Class: {selected or 'choose 1-5'} | saved: {saved}",
                (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
    cv2.imshow("Gesture dataset collector", shown)
    key = cv2.waitKey(1) & 0xFF

    if key in CLASSES:
        selected = CLASSES[key]
        out = RAW / selected / SESSION
        out.mkdir(parents=True, exist_ok=True)
        saved = len(list(out.glob("*.png")))
        print(f"Selected {selected}; output: {out}")
    elif key == 32:
        if selected is None:
            print("Select a class first (1-5).")
            continue
        out = RAW / selected / SESSION
        out.mkdir(parents=True, exist_ok=True)
        saved += 1
        path = out / f"{saved:05d}.png"
        cv2.imwrite(str(path), sample)
        print(f"Saved {path.relative_to(ROOT)}")
    elif key in (ord("q"), ord("Q")):
        break

cap.release()
cv2.destroyAllWindows()
