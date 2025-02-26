# Use an official Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy project files
COPY . /app

# Set environment variable for service account key
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/lithe-center-311717-a0bc84c5b67d.json

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI inside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
