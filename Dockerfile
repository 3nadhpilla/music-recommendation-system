# Use an official Python 3.10 slim image as base
FROM python:3.10-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt and install Python dependencies
# Using --no-cache-dir to keep the image small
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# If your app runs with `python app.py`
# Replace 'app.py' with your main application file
CMD ["python", "app.py"]

# If you have a Gunicorn server for a web app:
# CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT"]
# Replace 'app:app' with your actual WSGI entry point