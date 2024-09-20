# Use official Python image as a base
FROM python:3.11

# Update package list and install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the Django project files
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the Django server
CMD ["python", "-u", "manage.py", "runserver", "0.0.0.0:8000"]
