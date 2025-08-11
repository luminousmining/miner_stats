# Use an official Python image as base
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install cron and its dependencies
RUN apt-get update
RUN apt-get install -y cron git openssh-client

# Copy SSH key
COPY id_ed25519 /root/.ssh/id_ed25519
RUN chmod 600 /root/.ssh/id_ed25519
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts

# Install Python dependencies
RUN git clone git@github.com:luminousmining/miner_stats.git && \
    cd miner_stats && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Configure cron
RUN echo "0 11 * * * cd /app/miner_stats && python3 main.py && git commit -am 'update' && git push" > /etc/cron.d/daily-update
RUN chmod 0644 /etc/cron.d/daily-update
RUN crontab /etc/cron.d/daily-update

ARG GITHUB_TOKEN
RUN echo "GITHUB_TOKEN=$GITHUB_TOKEN"
ENV GITHUB_TOKEN=${GITHUB_TOKEN}

# Start cron in background
CMD ["sh", "-c", "cron && tail -f /dev/null"]
