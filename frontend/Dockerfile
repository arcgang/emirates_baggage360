# Frontend Dockerfile for Emirates Baggage360
# Build stage
FROM node:22 AS build

WORKDIR /app

# Copy dependency manifests
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Runtime stage with nginx
FROM nginx:alpine

# Accept backend host as build argument
ARG BACKEND_HOST=backend
ENV BACKEND_HOST=${BACKEND_HOST}

# Copy nginx configuration template
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Expose frontend port
EXPOSE 80
# x-preview-port marker for preview environment
# x-preview-port: 80

# nginx will substitute environment variables in templates and start
CMD ["nginx", "-g", "daemon off;"]
