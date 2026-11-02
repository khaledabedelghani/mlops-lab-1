
import argparse
import hashlib
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from src.food11.data import CLASSES

SPLITS = ("training", "validation", "evaluation")


def validate_dataset(dataset: Path, min_per_class: int, tau: float) -> bool:
    results = {}
    counts = {}
    seen_hashes = {}

    folder_errors = []
    image_errors = []
    count_errors = []
    duplicate_errors = []
    distribution_errors = []

    for split in SPLITS:
        split_dir = dataset / split

        if not split_dir.is_dir():
            folder_errors.append(f"Missing split: {split}")
            counts[split] = Counter()
            continue

        actual = {p.name for p in split_dir.iterdir() if p.is_dir()}
        expected = set(CLASSES)

        if actual != expected:
            folder_errors.append(
                f"{split}: missing={sorted(expected - actual)}, "
                f"extra={sorted(actual - expected)}"
            )

        counts[split] = Counter()

        for category in CLASSES:
            class_dir = split_dir / category

            if not class_dir.is_dir():
                count_errors.append(f"{split}/{category}: 0 images")
                continue

            images = sorted(
                p for p in class_dir.iterdir()
                if p.is_file() and p.suffix.lower() in
                {".jpg", ".jpeg", ".png"}
            )

            counts[split][category] = len(images)

            if len(images) < min_per_class:
                count_errors.append(
                    f"{split}/{category}: {len(images)} "
                    f"< {min_per_class}"
                )

            for path in images:
                try:
                    with Image.open(path) as img:
                        img.load()
                        if img.mode != "RGB" or img.size != (128, 128):
                            image_errors.append(
                                f"{path}: {img.mode}, {img.size}"
                            )
                except (UnidentifiedImageError, OSError, ValueError) as exc:
                    image_errors.append(f"{path}: {exc}")

                digest = hashlib.md5(path.read_bytes()).hexdigest()

                if digest in seen_hashes:
                    old_split, old_path = seen_hashes[digest]
                    if old_split != split:
                        duplicate_errors.append(
                            f"{old_path} and {path}"
                        )
                else:
                    seen_hashes[digest] = (split, path)

    train_total = sum(counts.get("training", {}).values())
    val_total = sum(counts.get("validation", {}).values())

    if train_total == 0 or val_total == 0:
        distribution_errors.append("Empty training or validation split")
    else:
        for category in CLASSES:
            train_share = counts["training"][category] / train_total
            val_share = counts["validation"][category] / val_total

            if abs(train_share - val_share) > tau:
                distribution_errors.append(
                    f"{category}: train={train_share:.4f}, "
                    f"validation={val_share:.4f}"
                )

    results["Class folders"] = folder_errors
    results["Image format and size"] = image_errors
    results["Minimum images per class"] = count_errors
    results["No cross-split duplicates"] = duplicate_errors
    results["Class distribution"] = distribution_errors

    for name, errors in results.items():
        print(f"{'PASS' if not errors else 'FAIL'} - {name}")
        for error in errors[:5]:
            print(f"  {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more")

    return all(not errors for errors in results.values())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--min-per-class", type=int, default=50)
    parser.add_argument("--tau", type=float, default=0.05)
    args = parser.parse_args()

    if not args.dataset.is_dir():
        print(f"FAIL - Dataset folder not found: {args.dataset}")
        sys.exit(1)

    success = validate_dataset(
        args.dataset,
        args.min_per_class,
        args.tau,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
