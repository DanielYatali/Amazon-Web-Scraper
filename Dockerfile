# Use an official Python runtime as a parent image
FROM python:3.11.5

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install Scrapyd
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir scrapyd

# Optionally install scrapyd-client to deploy the spiders from the container
# RUN pip install --no-cache-dir scrapyd-client

# Expose the default scrapyd port
EXPOSE 6800

# Run scrapyd when the container launches
CMD ["scrapyd"]
