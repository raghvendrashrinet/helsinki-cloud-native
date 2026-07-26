FROM alpine:latest

# Install bash and postgresql-client (for pg_dump)
RUN apk add --no-cache bash postgresql-client

# Create the directory explicitly
RUN mkdir -p /usr/src/app

# Copy your script
COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]   