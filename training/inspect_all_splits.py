
from pathlib import Path
import random
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPLIT = ROOT / "dataset" / "split"
OUTPUT = ROOT / "dataset_splits_preview.png"

random.seed(42)

split_names = ["train", "validation", "test"]
class_names = sorted(
    p.name for p in (SPLIT / "train").iterdir() if p.is_dir()
)

CELL = 144
HEADER = 30
COLS = 6

rows = len(class_names) * len(split_names)
canvas = np.full(
    (rows * (CELL + HEADER), COLS * CELL),
    255,
    dtype=np.uint8
)

for row, split_name in enumerate(split_names):
    for class_idx, class_name in enumerate(class_names):
        folder = SPLIT / split_name / class_name
        files = sorted(folder.glob("*.png"))

        selected = random.sample(files, min(COLS, len(files)))

        print(
            f"{split_name}/{class_name}: "
            f"{len(files)} images"
        )

        y = (row * len(class_names) + class_idx) * (CELL + HEADER)

        for col, path in enumerate(selected):
            image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)

            if image is None:
                continue

            resized = cv2.resize(
                image,
                (CELL, CELL),
                interpolation=cv2.INTER_NEAREST
            )

            x = col * CELL
            canvas[y + HEADER:y + HEADER + CELL, x:x + CELL] = resized

            cv2.putText(
                canvas,
                path.stem[-12:],
                (x + 3, y + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,
                (0, 0, 0),
                1
            )

        cv2.putText(
            canvas,
            f"{split_name} - {class_name}",
            (5, y + 12),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (0, 0, 0),
            1
        )

cv2.imwrite(str(OUTPUT), canvas)
print("\nSaved:", OUTPUT)
