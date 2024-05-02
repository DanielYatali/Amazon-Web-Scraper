# Use an official Python runtime as a parent image
FROM python:3.11.5

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Copy the current directory contents into the container at /usr/src/app
COPY default /app/default
COPY default /app/scrapy.cfg



# Install Scrapyd
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir scrapyd


# Make port 6800 available to the world outside this container
EXPOSE 6800

CMD echo "[scrapyd]\n\
http_port = $PORT\n\
bind_address = 0.0.0.0" > scrapyd.conf && \
scrapyd

# Define environment variable


