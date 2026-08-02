# Use a lightweight base image
FROM alpine:latest

RUN apk add --no-cache curl   
# Copy your local script into the image
COPY script.sh /script.sh

# Make the script executable
RUN chmod +x /script.sh

# Define the command to run when the container starts
CMD ["/script.sh"]
