# Use the official Python image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt .

# Copy the app code
COPY app/ /app/
COPY model/ /model/
COPY frontend/ /frontend/

RUN mkdir -p /app/results
RUN chmod -R 777 /app/

ENV PYTHONPATH="/:/model"

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run FastAPI
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
