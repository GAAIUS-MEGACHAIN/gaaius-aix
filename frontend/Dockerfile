# Frontend Dockerfile
FROM node:18-alpine as builder

WORKDIR /app/frontend

# Copy package files
COPY package.json yarn.lock* package-lock.json* ./

# Install dependencies
RUN npm install || yarn install

# Copy source code
COPY . .

# Build the app
RUN npm run build || yarn build

# Production stage
FROM node:18-alpine

WORKDIR /app/frontend

# Install serve to run the production build
RUN npm install -g serve

# Copy built app from builder
COPY --from=builder /app/frontend/build ./build

# Expose port
EXPOSE 3000

# Start the app
CMD ["serve", "-s", "build", "-l", "3000"]
