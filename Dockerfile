# Use an official Python runtime as a base image
#FROM python:3.9-slim
FROM python:3.9.21-alpine
# Set environment variables to prevent Python from writing .pyc files
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

# Copy the Django project files into the container
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Start the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
