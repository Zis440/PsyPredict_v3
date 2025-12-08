# Use Node.js for building
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files first (better caching)
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the code
COPY . .

# Expose the Vite port
EXPOSE 5173

# Run dev server (Add --host to allow Docker network access)
CMD ["npm", "run", "dev", "--", "--host"]