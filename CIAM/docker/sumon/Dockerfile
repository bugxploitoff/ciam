
# Use an debian-based image as the base
FROM debian:latest

# Install required packages
RUN apt-get update && \
    apt-get install -y dialog curl jq shellinabox

# Set a custom environment variable for a unique identifier
ENV CONTAINER_ID=sumon

# Copy the entrypoint script to the container
COPY entrypoint.sh ./entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Set the entrypoint script as the default entrypoint
ENTRYPOINT ["/entrypoint.sh"]
