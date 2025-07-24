FROM python:3.9-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    wget \
    unzip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Optional: decompress the model file
RUN if [ -f "model.bz2" ]; then bzip2 -d model.bz2; fi

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 10000
CMD ["python", "app.py"]
