# Use the official Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements and application code
COPY requirements.txt /app/
COPY app.py /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask uses
EXPOSE 5000

# Command to run the app
CMD ["python", " /home/ubuntu/presentasi-devops/tugas-devops/app.py"]
