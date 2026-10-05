**Lab 4 - Orchestrating the app with Docker Compose**

**Question 1**

**What happens to everything written to "/mlflow-data" if you never mount a volume there and just "docker run" this image standalone? Try it: run the container, register nothing, stop it, remove it, start a new one from the same image - what do you see in the UI?**

Without a volume, everything written to `/mlflow-data` is stored in the writable filesystem of that container.

Stopping the container does not delete the data, but removing the container removes its writable filesystem. Therefore, when a new container is started from the same image, it starts with a fresh MLflow database and the previous data is no longer visible in the UI.


**Question 2**

**Why a named volume here instead of a bind mount to a folder in your repo? Would a bind mount work just as well?**

A named volume is managed by Docker and stores the MLflow data independently from the container and from a specific folder on the host machine.

This makes the storage easier to manage and less dependent on host paths and permissions.

A bind mount would also work and would also persist the data, but it would be tied to a specific folder on the host machine.


**Question 3**

**In Lab 3 you had to use "host.docker.internal" or "--network host" to reach MLflow from inside the container. In this lab, "MLFLOW_TRACKING_URI" is "http://mlflow:5000". Why does that hostname resolve now when it didn't before?**

Docker Compose creates a private network for all the services in the Compose file.

Inside this network, Docker provides DNS resolution using service names.

Therefore, the hostname `mlflow` automatically resolves to the MLflow container, so the inference service can connect to MLflow using `http://mlflow:5000`.


**Question 4**

**Why does the frontend read "INFERENCE_URL" from an environment variable instead of hardcoding "http://inference:8000"?**

Using an environment variable makes the frontend portable and configurable.

Inside Docker Compose, `INFERENCE_URL` is set to `http://inference:8000`.

If the frontend is run outside Docker Compose, the inference URL can be changed to the address where the inference service is actually reachable, without changing the source code.


**Question 5**

**Only "mlflow" and "frontend" publish a port to the host. "inference" doesn't. Why not, and how does the frontend still reach it?**

MLflow and the frontend publish ports because they need to be accessed directly from the host machine.

The inference service is only accessed by the frontend, so it does not need a port published to the host.

The frontend and inference containers are connected to the same Docker Compose network, so the frontend can reach the inference service using its service name: `http://inference:8000`.


**Question 6**

**"depends_on" here only waits for the MLflow container process to start, not for the tracking server inside it to be ready. If "serve.py" tries to load the model at startup and MLflow isn't ready yet, what happens to the inference container?**

`depends_on` controls the startup order, but it does not guarantee that the MLflow server is ready to accept connections.

If the inference service tries to load the model before MLflow is ready, the connection or model-loading request can fail.

Because the model is loaded when the inference application starts, this failure can cause the inference process to exit and the container to stop.

A more robust solution would use a health check or retry mechanism.


**Question 7**

**Run "docker compose ps". Which services have a published port listed, and which don't? Does that match what you'd expect from the "docker-compose.yml"?**

The MLflow service has port `5000` published to the host.

The frontend service has port `8501` published to the host.

The inference service uses port `8000` internally, but it does not have a host port mapping.

This matches the configuration in `docker-compose.yml`.


**Question 8**

**Refresh the frontend and upload an image again. Does the prediction come from the new model version, or the old one? What command lets you pick up the new model version without rebuilding any image?**

Before restarting the inference service, it continues using the model version that was loaded when the inference process started.

Changing the model version or alias in MLflow does not automatically reload the model in the already running inference service.

The command used to load the new model version is:

`docker compose restart inference`

After the restart, the inference service loads the model currently referenced by the `champion` alias.

In this project, the `champion` alias is used instead of the legacy `Staging` stage.

In our test, version 2 was created by re-registering the same run, so the prediction itself may remain the same even though the registered model version changed.


**Question 9**

**Why does "restart" alone work here - no rebuild needed? What does that tell you about what's baked into the inference image versus fetched at container startup?**

A rebuild is not needed because the application code and Python dependencies did not change.

The inference image contains the application and its dependencies.

The model is resolved and loaded from MLflow when the inference container starts.

Therefore, restarting the inference service is enough to load the model version currently referenced in MLflow.


**Question 10**

**Is your registered model and its assignment still there after the "docker compose down" / "docker compose up" cycle? What happens with "docker compose down -v"?**

Yes. After `docker compose down` followed by `docker compose up`, the registered model and its `champion` alias, used in this project instead of the legacy `Staging` stage, were still available.

This happens because a normal `docker compose down` removes the containers and network but keeps the named volume.

In our test, the `champion` alias was still present after the normal down/up cycle.

When `docker compose down -v` is used, Docker also removes the named volume.

Because the MLflow database and artifacts are stored in this volume, removing the volume deletes the MLflow registry information and the stored artifacts.

After starting the stack again, the MLflow model registry was empty.


**Question 11**

**This compose file is still meant to run on one machine. What would have to change for the inference service to run as three replicas behind a load balancer, or for the MLflow service to survive a machine failure?**

Docker Compose can scale services on a single machine, but this setup does not provide multi-machine orchestration or high availability.

To run several inference replicas across multiple machines with load balancing and automatic recovery, an orchestrator such as Kubernetes or Docker Swarm would be needed.

MLflow would also need an external or shared persistent database and artifact storage so that its data is not tied to one machine and can survive a machine failure.