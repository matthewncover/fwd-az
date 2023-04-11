# Dockerfile
FROM python:3.8

# Set the working directory to /app
WORKDIR /fwd

# Copy the current directory contents into the container at /app
COPY . /fwd

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Run the script when the container launches
CMD ["bash", "-c", "python fwd/streamlit/main.py"]