FROM nginx:alpine
LABEL maintainer="Sanatana Dharma Archive"

# Copy website files to Nginx default document root
COPY . /usr/share/nginx/html

# Expose standard HTTP port
EXPOSE 80

# Run nginx in foreground
CMD ["nginx", "-g", "daemon off;"]

