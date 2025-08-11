FROM node:16-alpine

# Set working directory
WORKDIR /app

# Set environment variables
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV NEXT_PUBLIC_API_URL=http://localhost:8000

# Copy package files
COPY package.json ./

# Clean install dependencies
RUN npm ci || npm install

# Copy source code
COPY . .

# Build the application with verbose logging
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
