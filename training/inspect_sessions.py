
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "dataset" / "raw"
SPLIT = ROOT / "dataset" / "split"

split_names = ["train", "validation", "test"]

for class_dir in sorted(p for p in RAW.iterdir() if p.is_dir()):
    class_name = class_dir.name

    print("\n" + "=" * 60)
    print("CLASS:", class_name)
    print("=" * 60)

    sessions = {
        p.name: len(list(p.glob("*.png")))
        for p in class_dir.iterdir()
        if p.is_dir()
    }

    print("Raw sessions:")
    for name, count in sorted(sessions.items()):
        print(f"  {name}: {count} images")

    for split_name in split_names:
        folder = SPLIT / split_name / class_name
        files = list(folder.glob("*.png"))

        session_counts = defaultdict(int)

        for file in files:
            matched = False

            for session_name in sessions:
                prefix = session_name + "_"

                if file.name.startswith(prefix):
                    session_counts[session_name] += 1
                    matched = True
                    break

            if not matched:
                session_counts["UNKNOWN"] += 1

        print(f"\n{split_name.upper()}: {len(files)} images")
        for name, count in sorted(session_counts.items()):
            print(f"  {name}: {count} images")
