# ADos Mobile NetHunter Build Container
FROM ubuntu:22.04

LABEL maintainer="ADos Security Team"
LABEL description="Cross-platform build environment for ADos mobile cybersecurity OS"

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    tar \
    xz-utils \
    zip \
    unzip \
    curl \
    wget \
    ca-certificates \
    bc \
    bison \
    flex \
    build-essential \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

ENTRYPOINT ["python3", "build.py"]
CMD ["--help"]
