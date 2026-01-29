# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install system dependencies for OpenCV and video processing
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Create directory for data storage
RUN mkdir -p data/uploads data/output

# Make port 8000 available to the world outside this container
EXPOSE 7860

# Set Hugging Face specific environment variables
ENV USER=1000
ENV HOME=/home/user
RUN useradd -m -u 1000 user
RUN chown -R user:user /app
USER user

# Set environment variable for port
ENV PORT=7860

# Run the backend when the container launches
# Hugging Face uses port 7860 by default
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
