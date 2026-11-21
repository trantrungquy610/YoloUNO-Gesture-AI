
from pathlib import Path
import json
import cv2
import numpy as np
import tensorflow as tf

ROOT = Path(__file__).resolve().parents[1]
MODEL_KERAS = ROOT / "models" / "gesture_model.keras"
MODEL_TFLITE = ROOT / "models" / "gesture_model_int8.tflite"
LABELS_FILE = ROOT / "models" / "labels.json"
OUTPUT_DIR = ROOT / "test_samples"

if not MODEL_KERAS.exists() or not MODEL_TFLITE.exists():
    raise SystemExit("Không tìm thấy model .keras hoặc .tflite trong thư mục models!")

labels = json.loads(LABELS_FILE.read_text(encoding="utf-8"))

print("[INFO] Loading Keras model...")
keras_model = tf.keras.models.load_model(MODEL_KERAS)

print("[INFO] Loading TFLite model...")
interpreter = tf.lite.Interpreter(model_path=str(MODEL_TFLITE))
interpreter.allocate_tensors()

input_info = interpreter.get_input_details()[0]
output_info = interpreter.get_output_details()[0]

print("[INFO] Labels:", labels)
print("[INFO] TFLite input:", input_info["shape"], input_info["dtype"])
print("[INFO] TFLite input quantization:", input_info["quantization"])
print("[INFO] TFLite output:", output_info["shape"], output_info["dtype"])
print("[INFO] TFLite output quantization:", output_info["quantization"])

def preprocess(frame):
    # Giống webcam_sender.py
    frame = cv2.flip(frame, 1)
    h, w = frame.shape[:2]
    side = min(h, w) * 3 // 4
    x = (w - side) // 2
    y = (h - side) // 2
    crop = frame[y:y + side, x:x + side]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    return cv2.resize(gray, (64, 64), interpolation=cv2.INTER_AREA)

def predict_keras(image):
    x = image.astype(np.float32)[None, :, :, None]
    result = keras_model.predict(x, verbose=0)[0]
    return result

def predict_tflite(image):
    x = image[None, :, :, None]

    if input_info["dtype"] == np.uint8:
        x = x.astype(np.uint8)
    elif input_info["dtype"] == np.int8:
        scale, zero_point = input_info["quantization"]
        x = np.round(x.astype(np.float32) / scale + zero_point)
        x = np.clip(x, -128, 127).astype(np.int8)
    else:
        x = x.astype(input_info["dtype"])

    interpreter.set_tensor(input_info["index"], x)
    interpreter.invoke()
    result = interpreter.get_tensor(output_info["index"])[0]

    if output_info["dtype"] in (np.uint8, np.int8):
        scale, zero_point = output_info["quantization"]
        result = (result.astype(np.float32) - zero_point) * scale
    else:
        result = result.astype(np.float32)

    return result

def show_result(name, probabilities):
    order = np.argsort(probabilities)[::-1]
    print(f"\n--- {name} ---")
    for index in order:
        print(f"{labels[index]:12s}: {probabilities[index]:.4f}")

    print("Predicted:", labels[int(order[0])])

OUTPUT_DIR.mkdir(exist_ok=True)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise SystemExit("Không mở được webcam!")

print("\n========== LIVE MODEL TEST ==========")
print("Đưa cử chỉ vào khung hình rồi nhấn:")
print("1 = fist")
print("2 = no_hand")
print("3 = open_palm")
print("4 = thumbs_up")
print("5 = victory")
print("Q = thoát")
print("=====================================")

key_to_label = {
    ord("1"): "fist",
    ord("2"): "no_hand",
    ord("3"): "open_palm",
    ord("4"): "thumbs_up",
    ord("5"): "victory",
}

try:
    while True:
        ok, frame = cap.read()
        if not ok:
            print("[ERROR] Cannot read webcam frame")
            break

        image = preprocess(frame)
        preview = cv2.resize(image, (320, 320), interpolation=cv2.INTER_NEAREST)

        cv2.putText(
            preview, "Press 1-5 to capture | Q to quit",
            (5, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.42, 255, 1
        )
        cv2.imshow("Gesture Model Test - 64x64", preview)

        key = cv2.waitKey(1) & 0xFF

        if key in key_to_label:
            expected = key_to_label[key]
            print(f"\n\n========== CAPTURE: {expected} ==========")

            keras_result = predict_keras(image)
            tflite_result = predict_tflite(image)

            show_result("KERAS", keras_result)
            show_result("TFLITE INT8", tflite_result)

            save_path = OUTPUT_DIR / f"{expected}.png"
            cv2.imwrite(str(save_path), image)
            print("[SAVED]", save_path)

        elif key in (ord("q"), ord("Q")):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()

print("\n[INFO] Test finished.")
