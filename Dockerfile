# Use a Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements for the app
COPY requirements.txt .

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set the default command to run when starting the container
CMD ["python", "slack_scroll.py"]
