FROM python:3.9-slim-buster

WORKDIR /app

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
   && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /app

EXPOSE 8000 8501

RUN chmod 755 /

RUN pip install --no-cache-dir -U pip && \
   pip install --no-cache-dir numpy && \
   pip install --no-cache-dir -r requirements.txt
