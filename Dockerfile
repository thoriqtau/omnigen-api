# Stage 1: Builder
FROM python:3.9-slim AS builder

# Set environment variables for a clean Python environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements.txt for FastAPI app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Copy the OmniGen repository and install it
COPY OmniGen /app/OmniGen

# Download model_files dari Hugging Face
WORKDIR /app
RUN python3 -c "\
import torch; \
from diffusers import OmniGenPipeline; \
pipe = OmniGenPipeline.from_pretrained('Shitao/OmniGen-v1', torch_dtype=torch.bfloat16); \
pipe.save_pretrained('/app/model_files') \
"

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

# # Install OmniGen and FastAPI dependencies
# WORKDIR /app/OmniGen
# RUN pip install --upgrade pip
# RUN pip install -e /app/OmniGen
# WORKDIR /app

# Copy the FastAPI application code
COPY backend/handler.py /app/backend/handler.py

# Set the working directory to backend
WORKDIR /app/backend

CMD ["python3.9", "handler.py"]
