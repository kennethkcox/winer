# Stage 1: Build the frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

# Copy frontend package.json and install dependencies
COPY game-frontend-new/package.json game-frontend-new/package-lock.json ./
RUN npm ci

# Copy the rest of the frontend source code
COPY game-frontend-new/ ./

# Build the frontend
RUN npm run build

# Stage 2: Build the backend and create the final image
FROM python:3.9-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install backend dependencies
COPY game-backend-new/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user
RUN addgroup --system app && adduser --system --group app
USER app

# Copy the backend application code
COPY --chown=app:app game-backend-new/ ./

# Copy the built frontend assets from the frontend-builder stage
COPY --from=frontend-builder /app/frontend/out ./static
RUN chown -R app:app /app/static

# Expose the port
EXPOSE 8080

# Command to run the application
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
