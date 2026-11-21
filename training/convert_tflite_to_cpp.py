
from pathlib import Path

# Xác định thư mục dự án TrainAI
ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = ROOT / "models" / "gesture_model_int8.tflite"

OUTPUT_DIR = ROOT / "models" / "cpp_model"

HEADER_PATH = OUTPUT_DIR / "gesture_model_data.h"
SOURCE_PATH = OUTPUT_DIR / "gesture_model_data.cpp"

if not MODEL_PATH.exists():
    raise FileNotFoundError(MODEL_PATH)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Đọc model
model_data = MODEL_PATH.read_bytes()

# Chuyển byte sang hexadecimal
lines = []

for i in range(0, len(model_data), 12):
    chunk = model_data[i:i + 12]
    line = "    " + ", ".join(
        f"0x{b:02X}" for b in chunk
    )
    lines.append(line)

hex_data = ",\n".join(lines)

# Tạo header
header = """#pragma once

#include <cstddef>
#include <cstdint>

extern const unsigned char gesture_model_data[];
extern const size_t gesture_model_data_len;
"""

# Tạo source
source = f"""#include "gesture_model_data.h"

alignas(16) const unsigned char gesture_model_data[] = {{
{hex_data}
}};

const size_t gesture_model_data_len =
    sizeof(gesture_model_data);
"""

HEADER_PATH.write_text(header, encoding="utf-8")
SOURCE_PATH.write_text(source, encoding="utf-8")

print("========== CONVERSION SUCCESS ==========")
print(f"Model size : {len(model_data)} bytes")
print(f"Header     : {HEADER_PATH}")
print(f"Source     : {SOURCE_PATH}")
print("=========================================")
