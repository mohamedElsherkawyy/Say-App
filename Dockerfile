FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y tesseract-ocr libgl1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port (default for FastAPI/Uvicorn)
EXPOSE 8000

# Set environment variable for Tesseract path
ENV TESSERACT_CMD=/usr/bin/tesseract

# Run the FastAPI app with Uvicorn, always on port 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

