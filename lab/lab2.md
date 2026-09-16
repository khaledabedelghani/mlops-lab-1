# Lab 2 - Model training and experiment tracking with MLflow

## Question 1

**Look at "pyproject.toml" and "uv.lock". What changed?**

After installing the new libraries, "pyproject.toml" was updated to include the new project dependencies: "mlflow", "torch", "torchvision", and "scikit-learn".

It also contains the "pytorch-cpu" index configuration, so "torch" and "torchvision" are installed from the CPU-only PyTorch repository.

The "uv.lock" file was also updated. It now contains the exact resolved versions and dependency information for the new packages, including the CPU versions of PyTorch and Torchvision.

## Question 2

**What is "--backend-store-uri" used for? What is "--default-artifact-root" used for? What is the difference between the metadata MLflow stores and the artifacts it stores?**

"--backend-store-uri" specifies where MLflow stores the run metadata. In this lab, it uses the SQLite database "mlflow.db".

"--default-artifact-root" specifies where MLflow stores the artifacts produced by runs. In this lab, they are stored in the "mlruns/" folder.

Metadata includes information such as experiment names, run IDs, parameters, metrics, timestamps, and run status.

Artifacts are files produced by a run, such as trained models, plots, checkpoints, or other output files.

## Question 3

**Why shouldn't "mlflow.db" and "mlruns/" be tracked by Git, and why shouldn't they be tracked by DVC either?**

"mlflow.db" and "mlruns/" are local MLflow run outputs. They can change frequently whenever experiments are executed, so tracking them with Git would create unnecessary repository changes and large files.

They should not be tracked by DVC either because they are not versioned datasets. DVC is intended for data and model-related files that need reproducible versioning, while MLflow already manages experiment metadata and artifacts.

## Question 4

**What happens the first time you call "set_experiment" with a name that doesn't exist yet? Check the MLflow UI.**

The first time "mlflow.set_experiment('food11')" is called, MLflow checks whether the experiment already exists.

Since "food11" did not exist, MLflow automatically created a new experiment with that name.

After refreshing the MLflow UI, the new "food11" experiment appeared next to the "Default" experiment.

## Question 5

**What is the difference between "mlflow.log_param" and "mlflow.log_metric"? Why does "log_metric" take a "step" argument and "log_param" doesn't?**

"mlflow.log_param" is used to record values that are fixed for the whole run, such as the learning rate, batch size, number of epochs, or model architecture.

"mlflow.log_metric" is used to record values produced during or after training, such as loss or accuracy. These values can change during the run.

"log_metric" takes a "step" argument because the same metric can be logged several times, for example once after each epoch. The step indicates when the metric value was recorded.

"log_param" does not need a step because a parameter is normally set once at the beginning of the run and stays fixed.

## Question 6

**Open the run in the MLflow UI. Find the params, the metric charts, and the logged model artifact. Where does the model artifact actually live on disk?**

In the MLflow UI, the run contains the logged parameters such as the dataset, number of epochs, learning rate, batch size, model, and device.

The metric charts show the values logged during training, including "train_loss", "val_loss", and "val_accuracy" for each epoch, as well as the final "test_accuracy".

The trained model is also logged as an artifact. On disk, the model artifacts are stored inside the local "mlruns" directory, under the "food11" experiment's model folders.

For example, the model files are stored under paths of the form:

"C:\Users\khaled abed el ghani\OneDrive\Desktop\mlops-lab-1\mlruns\1\models\<model-id>\artifacts"

Each logged model has its own automatically generated model ID.

## Question 7

**In the MLflow UI, open the "food11" experiment. Select these runs and click "Compare". Which learning rate gave the best "val_accuracy"? Is higher always better?**

The learning rate "0.0001" gave the best validation accuracy, with a "val_accuracy" of 0.7856.

A higher learning rate was not always better. In these experiments, "0.01" gave the lowest validation accuracy, while reducing the learning rate to "0.0001" produced the best result.

## Question 8

**Use the parallel coordinates plot on the compare page to look at "lr", "batch_size" and "val_accuracy" together. What pattern do you see?**

The parallel coordinates plot shows that, with a batch size of 32, decreasing the learning rate improved the validation accuracy in these experiments.

The run with "lr=0.0001" and "batch_size=32" achieved the highest "val_accuracy" of 0.7856, while "lr=0.01" produced the lowest result.

For "lr=0.001", increasing the batch size from 32 to 64 also improved the final validation accuracy from 0.5201 to 0.6432.

## Question 9

**Sort the runs table by "val_accuracy" descending. Which run is the best one? Note its run ID, you'll need it in the next lab.**

After sorting the runs by "val_accuracy" in descending order, the best run is "selective-bass-972".

Its validation accuracy is approximately 0.7856.

The run ID is:

"a3e598453d2c4ca0beb78ad887c1aaa1"