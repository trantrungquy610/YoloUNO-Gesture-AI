"""Train a compact CNN from dataset/split/{train,validation}/<class>/*.png.
Run prepare_split.py first. Images are grayscale 64x64; model normalizes to [0,1].
"""
from pathlib import Path
import json
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

ROOT = Path(__file__).resolve().parents[1]
SPLIT = ROOT / "dataset" / "split"
OUT = ROOT / "models"
OUT.mkdir(exist_ok=True)
IMG = (64, 64)
BATCH = 32
SEED = 42

train = keras.utils.image_dataset_from_directory(
    SPLIT / "train", color_mode="grayscale", image_size=IMG,
    batch_size=BATCH, shuffle=True, seed=SEED, label_mode="int")
val = keras.utils.image_dataset_from_directory(
    SPLIT / "validation", color_mode="grayscale", image_size=IMG,
    batch_size=BATCH, shuffle=False, label_mode="int")
class_names = train.class_names
if len(class_names) != 5:
    raise SystemExit(f"Expected 5 classes, found {class_names}")

AUTOTUNE = tf.data.AUTOTUNE
train = train.cache().shuffle(500).prefetch(AUTOTUNE)
val = val.cache().prefetch(AUTOTUNE)

model = keras.Sequential([
    layers.Input(shape=(64, 64, 1), name="image"),
    layers.Rescaling(1.0 / 255.0),
    layers.Conv2D(8, 3, padding="same", activation="relu"),
    layers.MaxPooling2D(),
    layers.Conv2D(16, 3, padding="same", activation="relu"),
    layers.MaxPooling2D(),
    layers.Conv2D(24, 3, padding="same", activation="relu"),
    layers.GlobalAveragePooling2D(),
    layers.Dense(5, activation="softmax", name="probabilities"),
])
model.compile(optimizer=keras.optimizers.Adam(1e-3),
              loss="sparse_categorical_crossentropy", metrics=["accuracy"])
callbacks = [
    keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=8,
                                  restore_best_weights=True),
    keras.callbacks.ModelCheckpoint(OUT / "gesture_model.keras",
                                    monitor="val_accuracy", save_best_only=True),
]
model.fit(train, validation_data=val, epochs=60, callbacks=callbacks)
model.save(OUT / "gesture_model.keras")
(OUT / "labels.json").write_text(json.dumps(class_names, indent=2), encoding="utf-8")
print("Classes:", class_names)
print("Saved:", OUT / "gesture_model.keras")
