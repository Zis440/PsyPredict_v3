# 1. Use Node.js
FROM node:20-alpine

# 2. Set working directory
WORKDIR /app

# 3. Copy package files first (for faster builds)
COPY package.json package-lock.json ./
RUN npm install

# 4. Copy the rest of the code
COPY . .

# 5. Expose the port (5173 is standard for Vite)
EXPOSE 5173

# 6. Start the app (Host flag is crucial for Docker!)
CMD ["npm", "run", "dev", "--", "--host"]