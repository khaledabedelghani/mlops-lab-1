import argparse
import math
import os

import mlflow
from mlflow import MlflowClient


def get_accuracy(client, version):
    run = client.get_run(version.run_id)
    if "test_accuracy" not in run.data.metrics:
        raise ValueError(
            f"Version {version.version} has no test_accuracy metric"
        )
    return run.data.metrics["test_accuracy"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", type=int, required=True)
    args = parser.parse_args()

    mlflow.set_tracking_uri(
        os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
    )
    client = MlflowClient()

    candidate = client.get_model_version("food11", str(args.version))
    champion = client.get_model_version_by_alias("food11", "champion")

    if candidate.version == champion.version:
        raise ValueError("Candidate must be different from champion")

    candidate_acc = get_accuracy(client, candidate)
    champion_acc = get_accuracy(client, champion)

    champion_run = client.get_run(champion.run_id)
    if "test_samples" not in champion_run.data.metrics:
        raise ValueError("Champion is missing test_samples")

    n = int(champion_run.data.metrics["test_samples"])
    if n <= 0:
        raise ValueError("Test sample count must be positive")

    se = math.sqrt(champion_acc * (1 - champion_acc) / n)
    threshold = champion_acc + 2 * se

    if candidate_acc >= threshold:
        decision = "promoted"
        client.set_registered_model_alias(
            "food11", "champion", candidate.version
        )
    else:
        decision = "challenger"
        client.set_registered_model_alias(
            "food11", "challenger", candidate.version
        )

    client.set_model_version_tag(
        "food11", candidate.version, "promotion_decision", decision
    )
    client.set_model_version_tag(
        "food11", candidate.version,
        "candidate_test_accuracy", str(candidate_acc)
    )
    client.set_model_version_tag(
        "food11", candidate.version,
        "champion_test_accuracy", str(champion_acc)
    )

    print(f"Candidate accuracy: {candidate_acc:.4f}")
    print(f"Champion accuracy: {champion_acc:.4f}")
    print(f"Standard error: {se:.4f}")
    print(f"Required accuracy: {threshold:.4f}")
    print(f"Decision: {decision}")


if __name__ == "__main__":
    main()
