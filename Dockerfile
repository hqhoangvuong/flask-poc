# Use the official Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the TCP port that your app listens on
EXPOSE 8080

# Set the entry point for the container
CMD ["python", "app.py"]
