# Dockerfile for Hugging Face Space

# Use official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /home/user/app

# Copy requirements first
COPY server/requirements.txt ./server/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r server/requirements.txt

# Copy the rest of the app
COPY . .

# Expose port (if needed by FastAPI)
EXPOSE 7860

# Default command to run your app (FastAPI)
CMD ["python", "server/app.py"]