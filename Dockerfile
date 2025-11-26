FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files first
COPY . /app

# Install uv package manager and dependencies
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.local/bin/uv sync

# Add uv to PATH for runtime
ENV PATH="/root/.local/bin:$PATH"

EXPOSE 8000

CMD ["uv", "run", "python", "main.py"] 