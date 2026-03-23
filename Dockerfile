# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for Tkinter and GUI support
RUN apt-get update && apt-get install -y \
    python3-tk \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxinerama1 \
    libxi6 \
    libxkbcommon-x11-0 \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Set environment variables
# This tells Tkinter where to find the X server (host IP)
ENV DISPLAY=host.docker.internal:0.0

# Command to run the application
CMD ["python", "main.py"]
