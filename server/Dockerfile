# Use an official Python runtime as a parent image
FROM nikolaik/python-nodejs:latest

# Set the working directory in the container
WORKDIR /app

# Step 3: Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy the server code to /app
COPY server /app/server

# Verify installation of node and npm
RUN node -v && npm -v

# Install a specific version of Node.js
RUN npm install -g n
RUN n 20.12.0

# Update npm to the latest version
RUN npm install -g npm@latest


# Copy frontend code to /app/frontend
COPY frontend /app/frontend

# Install frontend dependencies and build the React app
RUN cd /app/frontend && \
    npm install && \
    npm run build

# Install Python dependencies
RUN cd /app/server && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Run app.py when the container launches
CMD ["python", "./server/app.py"]