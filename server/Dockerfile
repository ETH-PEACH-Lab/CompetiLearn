# Use an official Python runtime as a parent image
FROM python:3.12.4-slim

# Set the working directory in the container
WORKDIR /app

# Install necessary build tools and C++ compiler
RUN apt-get update && \
    apt-get install -y build-essential g++ curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs && \
    apt-get install -y npm && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Verify installation of node and npm
RUN node -v && npm -v

# Copy the server code to /app
COPY server /app/server

# Install Python dependencies
RUN cd /app/server && \
    pip install --no-cache-dir -r requirements.txt

# Copy frontend code to /app/frontend
COPY frontend /app/frontend

# Install frontend dependencies and build the React app
RUN cd /app/frontend && \
    npm install && \
    npm run build

# Copy build files to the Flask public directory
# RUN mkdir -p /app/public && \
#     cp -r /app/frontend/build/* /app/public/

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Run app.py when the container launches
CMD ["python", "./server/app.py"]