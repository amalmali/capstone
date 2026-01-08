# ============================
# Stage 1: Builder (install deps)
# ============================
FROM python:3.12-slim AS builder

# Create working directory
WORKDIR /app

# Install system deps required for Shapely and PostgreSQL client libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies list
COPY app/requirements.txt .

# Install Python packages to local user space to keep image slim
RUN pip install --user --no-cache-dir -r requirements.txt
RUN pip install uvicorn

# ============================
# Stage 2: Runtime
# ============================
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Add local bin to PATH
ENV PATH=/root/.local/bin:$PATH

# Copy FastAPI app code
COPY app .

# Expose FastAPI port
EXPOSE 8000

# Default startup command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]