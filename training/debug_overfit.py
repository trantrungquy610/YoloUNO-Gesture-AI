
from pathlib import Path
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

ROOT = Path(__file__).resolve().parents[1]
TRAIN_DIR = ROOT / "dataset" / "split" / "train"

ds = keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    color_mode="grayscale",
    image_size=(64, 64),
    batch_size=512,
    shuffle=True,
    seed=42,
    label_mode="int",
)

class_names = ds.class_names
images, labels = next(iter(ds))

images = images.numpy()
labels = labels.numpy()

# Chọn 20 ảnh cho mỗi lớp
selected = []

for class_id, class_name in enumerate(class_names):
    indices = np.where(labels == class_id)[0]
    selected.extend(indices[:20])

selected = np.array(selected)
x = images[selected]
y = labels[selected]

print("Selected:", x.shape)
print("Class distribution:", np.bincount(y))

# CNN mới: giữ lại thông tin vị trí bằng Flatten
model = keras.Sequential([
    layers.Input(shape=(64, 64, 1)),
    layers.Rescaling(1.0 / 255.0),

    layers.Conv2D(8, 3, padding="same", activation="relu"),
    layers.MaxPooling2D(),

    layers.Conv2D(16, 3, padding="same", activation="relu"),
    layers.MaxPooling2D(),

    layers.Conv2D(24, 3, padding="same", activation="relu"),
    layers.MaxPooling2D(),

    layers.Flatten(),
    layers.Dense(32, activation="relu"),
    layers.Dense(5, activation="softmax"),
])

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)

model.summary()

print("\n===== FLATTEN OVERFIT TEST =====")

model.fit(
    x,
    y,
    epochs=200,
    batch_size=10,
    shuffle=True,
    verbose=0,
)

loss, accuracy = model.evaluate(x, y, verbose=0)

predictions = np.argmax(model.predict(x, verbose=0), axis=1)

print(f"\nFinal loss: {loss:.4f}")
print(f"Final accuracy: {accuracy * 100:.2f}%")

print("\nConfusion matrix:")
print(tf.math.confusion_matrix(y, predictions).numpy())

print("\nPredicted class distribution:")
print(np.bincount(predictions, minlength=5))

print("\nClass order:", class_names)
