
from pathlib import Path
import random
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "dataset" / "split" / "train"
OUTPUT = ROOT / "dataset_train_preview.png"

random.seed(42)

classes = sorted(p.name for p in TRAIN.iterdir() if p.is_dir())

if not classes:
    raise SystemExit("Không tìm thấy các thư mục class trong dataset/split/train")

COLS = 6
CELL = 160
HEADER = 35

canvas = np.full(
    (len(classes) * (CELL + HEADER), COLS * CELL),
    255, dtype=np.uint8
)

for row, class_name in enumerate(classes):
    folder = TRAIN / class_name
    files = list(folder.glob("*.png"))
    selected = random.sample(files, min(COLS, len(files)))

    print(f"\n[{class_name}] Total images: {len(files)}")

    for col, path in enumerate(selected):
        image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)

        if image is None:
            print("Cannot read:", path)
            continue

        print(
            f"  {path.name}: min={image.min()}, "
            f"max={image.max()}, mean={image.mean():.2f}, "
            f"std={image.std():.2f}"
        )

        resized = cv2.resize(
            image, (CELL, CELL),
            interpolation=cv2.INTER_NEAREST
        )

        y = row * (CELL + HEADER)
        x = col * CELL

        canvas[y + HEADER:y + HEADER + CELL, x:x + CELL] = resized

        cv2.putText(
            canvas,
            class_name,
            (x + 5, y + 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 0, 0),
            1
        )

cv2.imwrite(str(OUTPUT), canvas)

print("\nSaved preview:", OUTPUT)
