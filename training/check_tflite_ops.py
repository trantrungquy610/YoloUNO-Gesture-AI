
from pathlib import Path
import tensorflow as tf

# Đường dẫn model
PROJECT_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_DIR / "models" / "gesture_model_int8.tflite"

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Không tìm thấy model: {MODEL_PATH}")

print("=" * 55)
print("KIỂM TRA TOÁN TỬ CỦA TFLITE MODEL")
print("=" * 55)

print(f"Model: {MODEL_PATH}")
print(f"Kích thước: {MODEL_PATH.stat().st_size:,} bytes")

# Đọc model
interpreter = tf.lite.Interpreter(
    model_path=str(MODEL_PATH)
)

# Lấy danh sách toán tử
ops = interpreter._get_ops_details()

print("\nDANH SÁCH TOÁN TỬ:")
print("-" * 55)

unique_ops = []

for index, op in enumerate(ops):
    name = op["op_name"]

    print(f"{index + 1:02d}. {name}")

    if name not in unique_ops:
        unique_ops.append(name)

print("\nDANH SÁCH TOÁN TỬ KHÔNG TRÙNG:")
print("-" * 55)

for name in unique_ops:
    count = sum(1 for op in ops if op["op_name"] == name)
    print(f"{name}: {count} lần")

print("\nTỔNG KẾT:")
print(f"Số node: {len(ops)}")
print(f"Số toán tử khác nhau: {len(unique_ops)}")

# Kiểm tra tensor
print("\nINPUT:")
for item in interpreter.get_input_details():
    print(
        f"Name={item['name']}, "
        f"Shape={item['shape']}, "
        f"Dtype={item['dtype']}"
    )

print("\nOUTPUT:")
for item in interpreter.get_output_details():
    print(
        f"Name={item['name']}, "
        f"Shape={item['shape']}, "
        f"Dtype={item['dtype']}"
    )

print("\nKIỂM TRA ALLOCATE TENSORS:")
try:
    interpreter.allocate_tensors()
    print("TensorFlow Lite AllocateTensors: SUCCESS")
except Exception as e:
    print("TensorFlow Lite AllocateTensors: FAILED")
    print(e)

print("\nHOÀN TẤT.")
