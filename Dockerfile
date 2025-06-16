# Use the Python 3 official image
# https://hub.docker.com/_/python
FROM python:3.9

# Run in unbuffered mode
ENV PYTHONUNBUFFERED=1 

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create and change to the app directory.
WORKDIR /app

# Copy local code to the container image.
COPY . ./

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the web service on container startup.
CMD ["python", "app_production.py"]