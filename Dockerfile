# Start with a slim, official Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy and install dependencies first to leverage Docker layer caching
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application source code
COPY . .

# Hugging Face Spaces sets the PORT environment variable to 7860
# Uvicorn will listen on this port
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]