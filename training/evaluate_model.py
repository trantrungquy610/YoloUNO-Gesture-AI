"""Evaluate saved Keras model on the held-out test split."""
from pathlib import Path
import json
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix

ROOT = Path(__file__).resolve().parents[1]
model = tf.keras.models.load_model(ROOT / "models" / "gesture_model.keras")
test = tf.keras.utils.image_dataset_from_directory(
    ROOT / "dataset" / "split" / "test", color_mode="grayscale",
    image_size=(64, 64), batch_size=32, shuffle=False, label_mode="int")
labels = test.class_names
truth, pred = [], []
for x, y in test:
    p = model.predict(x, verbose=0)
    truth.extend(y.numpy().tolist())
    pred.extend(np.argmax(p, axis=1).tolist())
print(classification_report(truth, pred, target_names=labels, digits=4))
print("Confusion matrix (rows=true, cols=pred):")
print(confusion_matrix(truth, pred))
