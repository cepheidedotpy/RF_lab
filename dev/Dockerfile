# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies for Tkinter/GUI, PyVISA backend, and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    tcl-dev \
    tk-dev \
    python3-tk \
    x11-apps \
    libusb-1.0-0-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the entire project content into the container
COPY . /app/

# Install Python packages
RUN pip install --no-cache-dir -r dev/requirements.txt

# --- Configuration for GUI and Instrument Communication ---
# Default to host.docker.internal for Windows (Xming/VcXsrv)
ENV DISPLAY=host.docker.internal:0.0
ENV QT_X11_NO_MITSHM=1

# Ensure Measurement and Config directories exist
RUN mkdir -p "/app/Measurement Data" "/app/ZVA config"

# Entrypoint: Start the app
CMD ["python", "-u", "dev/main.py"]
