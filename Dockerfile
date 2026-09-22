FROM python:3.13-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir uv==0.12.10

COPY pyproject.toml uv.lock ./

ENV UV_NO_INSTALL_PROJECT=1

RUN uv sync --frozen --no-dev


FROM python:3.13-slim AS runtime

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY src/ ./src/

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

ENTRYPOINT ["uvicorn", "src.food11.serve:app", "--host", "0.0.0.0", "--port", "8000"]