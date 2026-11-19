
"""Convert trained Keras CNN to full-integer INT8 TFLite."""
from pathlib import Path
import shutil
import numpy as np
import tensorflow as tf

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "gesture_model.keras"
SAVED_MODEL_PATH = ROOT / "models" / "saved_model_for_tflite"
OUTPUT_PATH = ROOT / "models" / "gesture_model_int8.tflite"

# 1. Load trained Keras model
model = tf.keras.models.load_model(MODEL_PATH)

# 2. Prepare representative dataset
train = tf.keras.utils.image_dataset_from_directory(
    ROOT / "dataset" / "split" / "train",
    color_mode="grayscale",
    image_size=(64, 64),
    batch_size=1,
    shuffle=True,
    label_mode=None,
)

def representative_dataset():
    for images in train.take(300):
        yield [images.numpy().astype(np.float32)]

# 3. Export Keras model to SavedModel
if SAVED_MODEL_PATH.exists():
    shutil.rmtree(SAVED_MODEL_PATH)

model.export(str(SAVED_MODEL_PATH))

# 4. Convert SavedModel to INT8 TFLite
converter = tf.lite.TFLiteConverter.from_saved_model(
    str(SAVED_MODEL_PATH)
)

converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_dataset
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS_INT8
]
converter.inference_input_type = tf.uint8
converter.inference_output_type = tf.uint8

content = converter.convert()

# 5. Save TFLite model
OUTPUT_PATH.write_bytes(content)
print(f"Saved: {OUTPUT_PATH}")
print(f"Model size: {len(content)} bytes")

# 6. Verify model
interpreter = tf.lite.Interpreter(model_content=content)
interpreter.allocate_tensors()

print("Input:", interpreter.get_input_details())
print("Output:", interpreter.get_output_details())
print("INT8 TFLite export completed successfully!")
