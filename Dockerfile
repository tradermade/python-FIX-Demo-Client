FROM python:3.11-slim

# Ensure system tools and Python utilities are installed
RUN apt-get update && apt-get install -y \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && ln -sf /usr/bin/pip3 /usr/bin/pip \
    && rm -rf /var/lib/apt/lists/*

# Install QuickFIX Python bindings
RUN pip install quickfix
RUN pip install dotenv

# Set working directory
WORKDIR /workspace
# Copy Python FIX client and config

# COPY spec /workspace/spec
COPY spec /workspace/spec




# Run FIX client
CMD ["python", "fix_client.py", "--configfile", "clientLocal.cfg"]
