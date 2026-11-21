
from pathlib import Path
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "gesture_model.keras"
SPLIT = ROOT / "dataset" / "split"

model = tf.keras.models.load_model(MODEL_PATH)

for split_name in ["train", "validation", "test"]:
    print("\n" + "=" * 55)
    print(f"DATASET: {split_name.upper()}")
    print("=" * 55)

    dataset = tf.keras.utils.image_dataset_from_directory(
        SPLIT / split_name,
        color_mode="grayscale",
        image_size=(64, 64),
        batch_size=32,
        shuffle=False,
        label_mode="int"
    )

    labels = dataset.class_names
    truth, pred = [], []

    for images, targets in dataset:
        probabilities = model.predict(images, verbose=0)
        truth.extend(targets.numpy().tolist())
        pred.extend(np.argmax(probabilities, axis=1).tolist())

    print("\nClass order:", labels)
    print("\nClassification report:")
    print(classification_report(
        truth, pred,
        target_names=labels,
        digits=4,
        zero_division=0
    ))

    print("Confusion matrix:")
    print(confusion_matrix(truth, pred))

    print("\nPredicted class counts:")
    for i, name in enumerate(labels):
        print(f"{name:12s}: {pred.count(i)}")
