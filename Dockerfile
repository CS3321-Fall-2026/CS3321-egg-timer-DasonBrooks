# Step 1: Python on Alpine Linux as the base image
FROM python:3.12-alpine

WORKDIR /app

# Step 2: install uv
RUN pip install --no-cache-dir uv

# Create the virtual env and "source" it for every later layer.
# (Each RUN is a fresh shell, so activating = putting the venv on PATH.)
ENV VIRTUAL_ENV=/app/.venv
RUN uv venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy the project in
COPY pyproject.toml README.md ./
COPY src ./src
COPY tests ./tests

# Step 3: install the project plus every extra/group (including dev tools).
# uv has no `--include-all` flag; `--all-extras --all-groups` is the equivalent.
RUN uv sync --all-extras --all-groups

# Step 4: run the tests - the build fails here if any test fails
RUN pytest

# Step 5: build a wheel out of the API, then install that wheel
RUN uv build --wheel \
    && uv pip install --force-reinstall --no-deps dist/*.whl

# Step 6: run the application
EXPOSE 8000
CMD ["uvicorn", "egg_timer.main:app", "--host", "0.0.0.0", "--port", "8000"]
