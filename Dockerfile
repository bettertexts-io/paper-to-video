FROM python:3.9-slim-buster

WORKDIR /app

# Install apt-utils
RUN apt-get update && \
   apt-get install -y apt-utils

# Install system-level dependencies
RUN set -x \
   && apt update \
   && apt upgrade -y \
   && apt-get install -y \
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
   sqlite3 \
   && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first for caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -U pip && \
   pip install --no-cache-dir numpy && \
   pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . /app

# Expose necessary ports
EXPOSE 8000 8501

# Set necessary permissions
RUN chmod 755 /
