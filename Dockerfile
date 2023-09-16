# Use a base image with preinstalled packages for faster builds
FROM python:3.9-slim-buster

WORKDIR /app

# Install system-level dependencies first for caching
RUN set -x \
   && apt update \
   && apt upgrade -y \
   && apt-get install -y \
   sqlite3=3.35.0 \
   build-essential \
   libcairo2-dev \
   libpango1.0-dev \
   libjpeg-dev \
   libgif-dev \
   librsvg2-dev \
   texlive \
   texlive-latex-extra \
   texlive-fonts-extra \
   texlive-latex-recommended \
   texlive-science \
   tipa \
   ffmpeg \
   libespeak-dev \
   build-essential \
   && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install python packages
RUN pip install --no-cache-dir -U pip && \
   pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . /app

# Expose necessary ports
EXPOSE 8000 8501

# Set necessary permissions
RUN chmod 755 /
