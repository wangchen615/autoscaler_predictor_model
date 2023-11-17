# Use an official Python runtime as a parent image
FROM python:3.8-slim
LABEL authors="chenw615"

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container at /usr/src/app
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . /usr/src/app

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME AUTOSCALER_MODEL_SERVER

# Run model_server.py when the container launches
CMD ["python", "./model_server.py"]