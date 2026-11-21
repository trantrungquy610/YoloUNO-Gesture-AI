"""Split whole recording sessions into train/validation/test sets.
Expected raw layout: dataset/raw/<class>/<session>/*.png
Requires at least 3 sessions per class. This prevents adjacent frames from
one capture session leaking across the evaluation sets.
"""
from pathlib import Path
import random
import shutil

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "dataset" / "raw"
OUT = ROOT / "dataset" / "split"
SEED = 42
random.seed(SEED)

classes = sorted(p.name for p in RAW.iterdir() if p.is_dir())
if len(classes) != 5:
    raise SystemExit(f"Expected 5 class folders in {RAW}; found {classes}")

if OUT.exists():
    shutil.rmtree(OUT)

for cls in classes:
    sessions = [p for p in (RAW / cls).iterdir() if p.is_dir()
                and any(p.glob("*.png"))]
    if len(sessions) < 3:
        raise SystemExit(
            f"Class '{cls}' has {len(sessions)} session(s). Collect at least "
            "3 separate sessions per class, then run this script again."
        )
    random.shuffle(sessions)
    n = len(sessions)
    n_test = max(1, round(n * 0.15))
    n_val = max(1, round(n * 0.15))
    if n_test + n_val >= n:
        n_test, n_val = 1, 1
    groups = {
        "test": sessions[:n_test],
        "validation": sessions[n_test:n_test + n_val],
        "train": sessions[n_test + n_val:],
    }
    for split, selected in groups.items():
        dest = OUT / split / cls
        dest.mkdir(parents=True, exist_ok=True)
        for session in selected:
            for src in session.glob("*.png"):
                shutil.copy2(src, dest / f"{session.name}_{src.name}")
    print(cls, {k: sum(len(list(s.glob('*.png'))) for s in v)
                for k, v in groups.items()})
print("Prepared session-separated dataset at", OUT)