# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Install dependencies from requirements.txt
RUN pip install -r requirements.txt

# Expose the port Django will run on
EXPOSE 8000

# Set the environment variable to tell Django to not use the production settings
ENV PYTHONUNBUFFERED 1

# Command to run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
