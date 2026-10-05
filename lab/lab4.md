\# Lab 4 - Orchestrating the app with Docker Compose



\## Question 1



\*\*What happens to everything written to "/mlflow-data" if you never mount a volume there and just "docker run" this image standalone? Try it: run the container, register nothing, stop it, remove it, start a new one from the same image — what do you see in the UI?\*\*



Without a volume, everything written to "/mlflow-data" is stored only inside the container.



If the container is removed, this data is lost. Starting a new container from the same image creates a fresh MLflow instance, so the previous data will not appear in the UI.





\## Question 2



\*\*Why a named volume here instead of a bind mount to a folder in your repo? Would a bind mount work just as well?\*\*



A named volume is managed by Docker and keeps the MLflow data independent from the container and the project folder.



A bind mount would also work and persist the data, but it depends on a specific host path and host permissions. A named volume is more convenient for persistent service data.





\## Question 3



\*\*In Lab 3 you had to use "host.docker.internal" or "--network host" to reach MLflow from inside the container. In this lab, "MLFLOW\_TRACKING\_URI" is "http://mlflow:5000". Why does that hostname resolve now when it didn't before?\*\*



Docker Compose creates a private network for all the services.



Inside this network, Docker provides DNS resolution using service names. Therefore, the hostname "mlflow" automatically resolves to the MLflow container, so "http://mlflow:5000" works.





\## Question 4



\*\*Why does the frontend read "INFERENCE\_URL" from an environment variable instead of hardcoding "http://inference:8000"?\*\*



Using an environment variable makes the frontend portable and configurable.



Inside Docker Compose, "INFERENCE\_URL" can be set to "http://inference:8000". If the frontend is run outside Docker Compose, another URL such as "http://127.0.0.1:8000" can be used without changing the source code.





\## Question 5



\*\*Only "mlflow" and "frontend" publish a port to the host. "inference" doesn't. Why not, and how does the frontend still reach it?\*\*



MLflow and the frontend publish ports because they need to be accessed directly from the host machine.



The inference service is only used by the frontend, so it does not need a published host port.



The frontend reaches the inference service through the private Docker Compose network using "http://inference:8000".





\## Question 6



\*\*"depends\_on" here only waits for the MLflow container process to start, not for the tracking server inside it to be ready. If "serve.py" tries to load the model at startup and MLflow isn't ready yet, what happens to the inference container?\*\*



"depends\_on" controls the startup order, but it does not guarantee that MLflow is ready to accept requests.



If the inference service tries to load the model before MLflow is ready, the request can fail and the inference container can exit.



The inference service can then be restarted after MLflow is ready. A more robust solution would use a health check or retry mechanism.





\## Question 7



\*\*Run "docker compose ps". Which services have a published port listed, and which don't? Does that match what you'd expect from the "docker-compose.yml"?\*\*



The MLflow service publishes port 5000 and the frontend service publishes port 8501.



The inference service uses port 8000 internally but does not publish it to the host.



This matches the configuration in "docker-compose.yml".





\## Question 8



\*\*Refresh the frontend and upload an image again. Does the prediction come from the new model version, or the old one? What command lets you pick up the new model version without rebuilding any image?\*\*



The inference service keeps using the model that was loaded when it started. Changing the model version or alias does not automatically reload the already running inference process.



The command used to load the new model version is:



"docker compose restart inference"



In this project, the "champion" alias is used instead of the legacy "Staging" stage. Restarting the inference service makes it load the model currently referenced by "champion".





\## Question 9



\*\*Why does "restart" alone work here — no rebuild needed? What does that tell you about what's baked into the inference image versus fetched at container startup?\*\*



A rebuild is not needed because the application code and dependencies did not change.



The inference image contains the application and its dependencies, while the model is fetched from MLflow when the container starts.



Therefore, restarting the inference service is enough to load the current model version from MLflow.





\## Question 10



\*\*Is your registered model and its assignment still there after the "docker compose down" / "docker compose up" cycle? What happens with "docker compose down -v"?\*\*



Yes. After "docker compose down" followed by "docker compose up", the registered model was still available because the named volume was preserved.



In our test, the "champion" alias still existed after the normal down/up cycle.



After running "docker compose down -v", Docker also removed the named volume.



As a result, the MLflow database, model registry information, and artifacts stored in the volume were removed. After starting the stack again, the model registry was empty.





\## Question 11



\*\*This compose file is still meant to run on one machine. What would have to change for the inference service to run as three replicas behind a load balancer, or for the MLflow service to survive a machine failure?\*\*



Docker Compose is mainly designed for services running on one machine.



To run several inference replicas on multiple machines with load balancing and fault tolerance, an orchestrator such as Kubernetes or Docker Swarm would be needed.



MLflow would also need shared or external persistent storage and a reliable external database so its data can survive the failure of one machine.

