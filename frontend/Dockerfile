# Use the official Node.js image as a base
FROM node:22.8.0

# Set the working directory inside the container
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the application code into the container
COPY . .

# Build the React app
RUN npm run build

# Install a simple HTTP server to serve the static files
RUN npm install -g serve

# Expose port 3000 for the React app
EXPOSE 3000

# Serve the built React app
CMD ["serve", "-s", "build", "-l", "3000"]