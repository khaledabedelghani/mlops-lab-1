import shutil
from pathlib import Path

from PIL import Image

RAW_DIR = Path("data/food11_raw")
PROCESSED_DIR = Path("data/food11_processed")
MINI_DIR = Path("data/food11_processed_mini")

SPLITS = ["training", "evaluation", "validation"]

CATEGORY_NAMES = {
    "0": "Bread",
    "1": "Dairy product",
    "2": "Dessert",
    "3": "Egg",
    "4": "Fried food",
    "5": "Meat",
    "6": "Noodles-Pasta",
    "7": "Rice",
    "8": "Seafood",
    "9": "Soup",
    "10": "Vegetable-Fruit",
}

CLASSES = [CATEGORY_NAMES[str(i)] for i in range(11)]


def category_from_filename(filename: str) -> str:
    """Return the food category from the image filename."""
    class_id = Path(filename).stem.split("_")[0]
    return CATEGORY_NAMES[class_id]


def resize_image(img: Image.Image, size: int = 128) -> Image.Image:
    """Return an RGB image resized to size x size."""
    return img.convert("RGB").resize((size, size))


def prepare_folder(folder):
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True, exist_ok=True)


def process_images():
    prepare_folder(PROCESSED_DIR)
    prepare_folder(MINI_DIR)

    for split in SPLITS:
        source_folder = RAW_DIR / split
        class_counts = {}

        for image_path in source_folder.glob("*.jpg"):
            class_name = category_from_filename(image_path.name)

            processed_class = PROCESSED_DIR / split / class_name
            mini_class = MINI_DIR / split / class_name

            processed_class.mkdir(parents=True, exist_ok=True)
            mini_class.mkdir(parents=True, exist_ok=True)

            with Image.open(image_path) as image:
                image = resize_image(image)

                output_path = processed_class / image_path.name
                image.save(output_path)

                class_counts[class_name] = class_counts.get(class_name, 0) + 1

                if class_counts[class_name] <= 100:
                    mini_path = mini_class / image_path.name
                    image.save(mini_path)

    print("Data preparation completed.")


if __name__ == "__main__":
    process_images()