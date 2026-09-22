# Lab 3 - Answers

## Question 1

The registered model was given version 1.

A logged model artifact belongs to one specific MLflow run. A registered model gives the model a shared name, such as `food11`, and allows multiple numbered versions to be managed independently from the runs that created them.

## Question 2

MLflow aliases such as `champion` and `challenger` replace the old built-in stages such as Staging and Production.

Versioning the model separately from the run allows several trained model versions to be managed under the same registered model name. An alias is flexible because it can be reassigned to another version without changing the application code.

## Question 3

Using `models:/food11@champion` avoids hard-coding a local `.pth` file path and lets the application load the model through the MLflow Model Registry.

To serve a newer model version, the `champion` alias can be reassigned to the newer version. The serving code does not need to change.

## Question 4

`pyproject.toml` and `uv.lock` are copied before the source code so Docker can cache the dependency installation layer.

If only a line in `serve.py` changes, Docker can reuse the cached `uv sync` layer and only rebuild the later layers that contain the source code.

## Question 5

The naive single-stage image had a content size of 469 MB, while the multi-stage image had a content size of 438 MB.

The multi-stage build therefore reduced the content size by 31 MB, about 6.6%.

Docker history showed that the largest layer was the Python virtual environment and dependencies: about 1.53 GB uncompressed in the naive image and 1.48 GB in the multi-stage image.

The naive image also kept the approximately 60.5 MB `uv` installation layer, while the final runtime stage did not.

## Question 6

Without a `.dockerignore`, unnecessary files are sent to the Docker daemon, which increases the build context size and slows down builds. If these files are copied into the image, they can also increase the final image size.

In this project, a file inside `__pycache__` already caused the Docker build context to fail. A host `.venv` can also cause problems if it is copied into a Linux container because the local Windows virtual environment is not compatible with Linux.

Folders such as `data`, `mlruns`, and `.git` mainly make the build context unnecessarily large when they are not needed.

## Question 7

Inside a Docker container, `127.0.0.1` refers to the container itself, not the host computer.

On Windows and macOS, `host.docker.internal` resolves to the host machine, allowing the container to reach the MLflow server running on the host.

## Question 8

Yes. After stopping the container and starting a new container from the same `food11-api:latest` image, the application and model loaded correctly without rebuilding the image.

This shows that the application code and Python dependencies are baked into the Docker image, while the model referenced by `food11@champion` is loaded from MLflow at runtime.

In this local setup, the `mlruns` directory was also mounted because the registered model artifact used a local Windows file path.

## Question 9

The Docker image currently exists only on the local machine.

Before another machine, CI runner, or Kubernetes cluster can reliably run the exact image, the image should be pushed to a container registry such as Docker Hub or another registry.

A versioned or immutable tag should be used, and preferably the image should be referenced by its SHA256 digest so the exact same image can be pulled.
