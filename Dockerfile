# Dockerfile pour NMAP-AI - Exécution sécurisée en sandbox
FROM ubuntu:22.04

# Install nmap and dependencies
RUN apt-get update && apt-get install -y \
    nmap \
    iputils-ping \
    curl \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 nmap_user

# Set working directory
WORKDIR /scans

# Change ownership
RUN chown -R nmap_user:nmap_user /scans

# Switch to non-root user
USER nmap_user

# Default command - prevent execution of dangerous commands
ENTRYPOINT ["nmap"]
CMD ["--version"]