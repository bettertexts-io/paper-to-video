FROM python:3.11-bookworm

WORKDIR /app

RUN set -x \
   && apt update

RUN set -x \
   && apt upgrade -y

RUN apt-get install -y \
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
   && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN chmod 755 /

RUN pip install -U pip
RUN pip install -r requirements.txt

# Define the ENTRY environment variable with a default value
ENV ENTRY=src/app.py
ENV EVIRONMENT=production

RUN chmod u+x docker-entry.sh

# Run the Python script specified by the ENTRY environment variable
CMD ./docker-entry.sh "$ENTRY"
