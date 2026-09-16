import argparse
from pathlib import Path

import mlflow
import mlflow.pytorch
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
from torchvision.models import ResNet18_Weights


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["processed", "mini"], default="mini")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--batch-size", type=int, default=32)
    return parser.parse_args()


def create_dataloader(folder, transform, batch_size, shuffle=False):
    dataset = datasets.ImageFolder(folder, transform=transform)

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=0,
    )


def evaluate(model, loader, criterion, device):
    model.eval()

    total_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            total_loss += loss.item() * images.size(0)

            predictions = outputs.argmax(dim=1)
            correct += (predictions == labels).sum().item()
            total += labels.size(0)

    average_loss = total_loss / total
    accuracy = correct / total

    return average_loss, accuracy


def main():
    args = parse_args()

    project_root = Path(__file__).resolve().parents[2]

    if args.dataset == "mini":
        dataset_root = project_root / "data" / "food11_processed_mini"
    else:
        dataset_root = project_root / "data" / "food11_processed"

    train_dir = dataset_root / "training"
    val_dir = dataset_root / "validation"
    test_dir = dataset_root / "evaluation"

    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )

    train_loader = create_dataloader(
        train_dir,
        transform,
        args.batch_size,
        shuffle=True,
    )

    val_loader = create_dataloader(
        val_dir,
        transform,
        args.batch_size,
    )

    test_loader = create_dataloader(
        test_dir,
        transform,
        args.batch_size,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = models.resnet18(weights=ResNet18_Weights.DEFAULT)

    model.fc = nn.Linear(
        model.fc.in_features,
        11,
    )

    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("food11")

    with mlflow.start_run():
        mlflow.log_params(
            {
                "dataset": args.dataset,
                "epochs": args.epochs,
                "lr": args.lr,
                "batch_size": args.batch_size,
                "model": "resnet18",
                "device": str(device),
            }
        )

        for epoch in range(args.epochs):
            model.train()

            total_train_loss = 0.0
            total_train_samples = 0

            for images, labels in train_loader:
                images = images.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()

                outputs = model(images)
                loss = criterion(outputs, labels)

                loss.backward()
                optimizer.step()

                total_train_loss += loss.item() * images.size(0)
                total_train_samples += images.size(0)

            train_loss = total_train_loss / total_train_samples

            val_loss, val_accuracy = evaluate(
                model,
                val_loader,
                criterion,
                device,
            )

            mlflow.log_metric(
                "train_loss",
                train_loss,
                step=epoch,
            )

            mlflow.log_metric(
                "val_loss",
                val_loss,
                step=epoch,
            )

            mlflow.log_metric(
                "val_accuracy",
                val_accuracy,
                step=epoch,
            )

            print(
                f"Epoch {epoch + 1}/{args.epochs} | "
                f"train_loss={train_loss:.4f} | "
                f"val_loss={val_loss:.4f} | "
                f"val_accuracy={val_accuracy:.4f}"
            )

        _, test_accuracy = evaluate(
            model,
            test_loader,
            criterion,
            device,
        )

        mlflow.pytorch.log_model(
            model,
            name="model",
            serialization_format="pickle",
)

        print(f"Test accuracy: {test_accuracy:.4f}")


if __name__ == "__main__":
    main()