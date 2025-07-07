
FROM nginx:alpine

# Clean default nginx HTML files
RUN rm -rf /usr/share/nginx/html/*

# Copy your static files into the container
COPY ./frontend /usr/share/nginx/html

# Copy nginx configuration for metrics endpoint
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80 (optional – handled by Kubernetes later)
EXPOSE 80

# Use default Nginx CMD (already defined in base image)
