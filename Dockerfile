# Use an official, lightweight Python runtime
FROM python:3.10-slim

# Set working directory for the installation phase
WORKDIR /build

# Install essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install uv (The lightning-fast Python package manager)
RUN pip install --no-cache-dir uv

# Copy the modern dependency configuration files
COPY pyproject.toml uv.lock ./

# Install dependencies directly into the system Python using uv
RUN uv pip install --system -r pyproject.toml

# ==========================================
# HUGGING FACE SPACES SECURITY PROTOCOL
# ==========================================
# Hugging Face requires Docker spaces to run as a non-root user (UID 1000)
RUN useradd -m -u 1000 user
USER user

# Set up the non-root user's environment variables
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Move working directory to the user's home folder
WORKDIR $HOME/app

# Copy the rest of the application code and assign ownership to the non-root user
COPY --chown=user . .

# Expose the mandatory Hugging Face port
EXPOSE 7860

# Command to boot the FastAPI WebSockets server
# We use the module syntax to ensure proper path resolution
CMD ["python", "-m", "server.app"]