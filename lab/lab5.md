# Lab 5 - CI/CD with GitHub Actions

## Q1. Why is it a bad idea for a unit test to load the real model from your MLflow server? List at least two ways the test could fail even though your code is correct.

Unit tests should be fast, isolated, and reliable. A test could fail because the MLflow server is offline or the model artifact is unavailable, even if the application code is correct. Loading a real model also makes tests slower and increases resource usage.

## Q2. The fake model always answers "Bread" with 0.90 confidence. What exactly does `test_predict_returns_valid_json` prove, and what does it not prove?

The test verifies that the API accepts an image, processes the model prediction, and returns valid JSON with the expected category and confidence.

It does not prove that the real machine learning model is accurate or that the MLflow connection works.

## Q3. Which check caught it? Why is a train/test duplicate more dangerous than a corrupted image, even though the corrupted image makes the training script crash and the duplicate does not?

The cross-split duplicate detection check caught the copied image by comparing MD5 hashes.

A duplicate between training and evaluation causes data leakage. The model may appear more accurate because it has already seen the image during training. A corrupted image can cause a visible error, but a duplicate may silently produce misleading evaluation results.

During local validation, 43 cross-split duplicates were also detected in the original mini dataset.

## Q4. Your CI runner cannot see your data (it is in DVC, and maybe in a local remote). Where in your workflow should validate_data.py run so that it still protects you? Give two places.

First, run validation locally before committing or pushing new dataset versions.

Second, run validation in a separate data pipeline or a CI job with access to the DVC remote. After downloading the dataset, the job can execute validate_data.py.

The normal GitHub CI workflow can still run unit tests and Docker smoke tests without the full dataset.

## Q5. The `smoke` job has `needs: test`. What happens to it if a unit test fails? What would happen without `needs`?

If a unit test fails, the `test` job fails and the `smoke` job is skipped because `smoke` depends on `test`.

Without `needs: test`, the two jobs can run independently, so the smoke test might execute even if the unit tests fail.

This dependency avoids unnecessary Docker builds when the code has already failed its tests.

## Q6. How long did the whole run take? Run it a second time (push an empty commit with `git commit --allow-empty -m "ci"`) and compare. Which step got faster, and why?

First successful run (CI/CD #1): 2m 21s.
Empty-commit run (CI/CD #4): 2m 25s.

The workflow uses caching through `astral-sh/setup-uv`. When the dependency cache is reused, dependency installation may become faster because packages do not need to be downloaded again.

The empty-commit run was 4 seconds slower overall. Run tests became faster (12s to 11s), Run Ruff became faster (1s to 0s), and Install Python became faster (1s to 0s). However, Install dependencies took 5s instead of 4s, and Build Docker image took 77s instead of 76s. Although setup-uv supports caching, this comparison does not show a dependency installation speedup. Small differences may come from runner and build variability.

## Q7. This answers Question 9 of Lab 3. Why tag with the commit SHA rather than `latest`? Describe a concrete situation where `latest` leads two machines to run different code.

A Git commit SHA identifies the exact source-code version used to build a Docker image. This makes deployment reproducible and helps with debugging and rollback.

For example, Machine A downloads `latest` on Monday. On Tuesday, a new image is published with the same `latest` tag. Machine B downloads `latest` on Tuesday.

Both machines use the tag `latest`, but they may run different code.

Using the commit SHA avoids this ambiguity.

## Q8. Why does the `push` job declare `permissions:` explicitly? What could a compromised step do with a token that had write access to everything in the repo?

The workflow explicitly defines permissions to follow the principle of least privilege.

`contents: read` allows the workflow to read repository contents, while `packages: write` allows it to publish the image to GitHub Container Registry.

If a compromised workflow step had unrestricted write permissions, it could potentially modify repository content, change workflows, or overwrite published packages.

Restricting the token reduces the security risk.

## Q9. What does the pull request page show? Could you still merge? What does that change for a team compared to "everybody runs the tests on their laptop before pushing"?

When we intentionally introduced a failing test, GitHub Actions showed a failed `test` check. The dependent `smoke` job could not proceed normally.

After fixing the test and pushing the correction, both `test` and `smoke` passed.

If branch protection is configured and enforced, a pull request with failing required checks cannot be merged normally. Without enforced protection, merging may still be possible.

For a team, automated checks provide a consistent quality gate. Developers no longer need to rely only on everyone remembering to run tests locally.

The Branches settings page showed no classic branch protection rule. On our pull request, the Merge pull request button was available even while the smoke check was still running. This suggests that successful checks are not currently enforced as a mandatory merge requirement. The team should configure required status checks for main using branch protection or a ruleset.

## Q10. For each candidate, what did the gate decide, and with which numbers? With your test-set size, how many accuracy points does `2 * se` represent?

Our evaluation dataset contains 1,096 images.

The current champion is version 1, with a test accuracy of 0.8075 (80.75%).

The standard error is calculated as:

`se = sqrt(p * (1 - p) / n)`

Using p = 0.8075 and n = 1096:

`se = 0.0119`

`2 * se = 0.0238`

This corresponds to approximately 2.38 percentage points.

The promotion threshold is:

`0.8075 + 0.0238 = 0.8313`

A candidate must reach approximately 83.13% test accuracy to replace the champion.

Candidate 1 - Version 2:

- Training: 1 epoch, learning rate 0.00001, batch size 32.
- Candidate accuracy: 20.16%.
- Champion accuracy: 80.75%.
- Required accuracy: 83.13%.
- Decision: challenger.

Candidate 2 - Version 3:

- Training: 5 epochs, learning rate 0.001, batch size 32.
- Candidate accuracy: 57.66%.
- Champion accuracy: 80.75%.
- Required accuracy: 83.13%.
- Decision: challenger.

Neither candidate reached the threshold. Version 1 remains champion. Version 3 is the current challenger, and both candidate versions have their decisions recorded in MLflow tags.

## Q11. `promote.py` needs to reach your MLflow server, so it cannot run in GitHub's cloud runners while MLflow lives on your laptop. Name two ways to make it run automatically after training.

First solution: Use a self-hosted GitHub Actions runner on a machine that can access the local MLflow server. After training finishes, the runner can execute `promote.py`.

Second solution: Use a hosted MLflow tracking server, such as DagsHub. GitHub Actions can connect to it using its tracking URI and credentials, then automatically execute the promotion script.

Both solutions allow model promotion to run automatically after training.

## Q12. Draw the pipeline you now have, from `git push` to a running container. Mark which steps are automatic, which still need a human, and where the code version and the model version are decided.

### CI/CD Pipeline Diagram

```text
Developer
   |
   | git push / Pull Request
   v
GitHub Actions [AUTOMATIC]
   |
   v
TEST JOB
   | Ruff lint
   | Unit tests
   | API tests with fake model
   v
SMOKE JOB [AUTOMATIC]
   | Runs only after test succeeds
   | Docker image build
   | Start container with SKIP_MODEL=1
   | Check /health endpoint
   v
Push to main?
   |
   +--- NO ---> No image publishing
   |
   +--- YES
         |
         v
   PUBLISH JOB [AUTOMATIC]
         |
         | Build and push Docker image
         | Tag with Git commit SHA
         v
   GitHub Container Registry
         |
         | Human/manual deployment
         v
   Running FastAPI Container
         |
         | Loads the selected model
         v
   MLflow Model Registry
         |
         +--> food11@champion
```

### Automatic steps

GitHub Actions automatically runs linting, unit tests, and Docker smoke tests on pushes and pull requests.

After a successful push to `main`, the workflow also publishes a Docker image to GHCR using the Git commit SHA.

### Human steps

A developer reviews and merges the pull request. The current workflow does not automatically deploy the published image to a running server.

Training and model promotion are currently separate from GitHub CI.

### Code version

The code version is determined by the Git commit SHA used to build and tag the Docker image.

### Model version

The model version is selected by the MLflow alias `champion`.

The `promote.py` script compares a candidate model's test accuracy against the champion, using the quality threshold.

If the candidate passes, it becomes the new champion. Otherwise, it receives the `challenger` alias.

The running container must have access to the configured MLflow tracking server to load the champion model.
