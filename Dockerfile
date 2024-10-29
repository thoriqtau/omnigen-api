# Stage 1: Builder
FROM python:3.9-slim AS builder

# Set environment variables for a clean Python environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the OmniGen repository and install it
COPY OmniGen /app/OmniGen

# Copy the model_files directly into the builder stage
COPY model_files /app/model_files

# Copy the requirements.txt for FastAPI app
COPY requirements.txt /app/requirements.txt

# Stage 2: Runtime
FROM python:3.9-slim

# Environment variables for a clean Python environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install only necessary system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy OmniGen, model files, and requirements from the builder stage
COPY --from=builder /app/OmniGen /app/OmniGen
COPY --from=builder /app/model_files /app/model_files
COPY --from=builder /app/requirements.txt /app/requirements.txt

# Install OmniGen and FastAPI dependencies
WORKDIR /app/OmniGen
RUN pip install --upgrade pip
RUN pip install -e /app/OmniGen
WORKDIR /app
RUN pip install -r requirements.txt

# Copy the FastAPI application code
COPY backend/handler.py /app/backend/handler.py

# Set the working directory to backend
WORKDIR /app/backend

RUN python3.9 handler.py

CMD ["python3.9", "handler.py"]
