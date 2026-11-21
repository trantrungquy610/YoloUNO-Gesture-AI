
from pathlib import Path
import random
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPLIT = ROOT / "dataset" / "split"
OUTPUT = ROOT / "problem_classes_preview.png"

random.seed(42)

splits = ["train", "validation", "test"]
classes = ["no_hand", "thumbs_up"]

CELL = 128
HEADER = 28
COLS = 6
SAMPLES = 12

# Mỗi nhóm gồm 12 ảnh, chia thành 2 hàng.
GROUP_HEIGHT = HEADER + 2 * CELL
canvas = np.full(
    (len(splits) * len(classes) * GROUP_HEIGHT,
     COLS * CELL),
    255,
    dtype=np.uint8
)

for split_idx, split_name in enumerate(splits):
    for class_idx, class_name in enumerate(classes):
        folder = SPLIT / split_name / class_name
        files = sorted(folder.glob("*.png"))

        selected = random.sample(
            files, min(SAMPLES, len(files))
        )

        group_idx = split_idx * len(classes) + class_idx
        y_base = group_idx * GROUP_HEIGHT

        title = f"{split_name.upper()} - {class_name}"
        cv2.putText(
            canvas, title, (5, y_base + 19),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, 0, 1
        )

        print(f"{title}: {len(files)} images")

        for i, path in enumerate(selected):
            image = cv2.imread(
                str(path), cv2.IMREAD_GRAYSCALE
            )

            if image is None:
                continue

            image = cv2.resize(
                image, (CELL, CELL),
                interpolation=cv2.INTER_NEAREST
            )

            row = i // COLS
            col = i % COLS

            y = y_base + HEADER + row * CELL
            x = col * CELL

            canvas[y:y + CELL, x:x + CELL] = image

            # Ghi mã timestamp để nhận biết phiên ghi hình.
            cv2.putText(
                canvas,
                path.stem[:15],
                (x + 2, y + CELL - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.3, 0, 1
            )

cv2.imwrite(str(OUTPUT), canvas)
print("\nSaved:", OUTPUT)
