# Base Ubuntu image
FROM ubuntu:22.04

LABEL maintainer="aidenfmunro"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    build-essential \
    cmake \
    ninja-build \
    git \
    python3 \
    unzip \
    zlib1g-dev \
    libbz2-dev \
    liblzma-dev \
    libfmt-dev \
    nlohmann-json3-dev \
    curl \
    wget \
    zip \
    unzip \ 
    tar \
    pkg-config \
    parallel \
    python3 \
    aria2 \
    && apt clean && rm -rf /var/lib/apt/lists/*

WORKDIR /root

RUN git clone --recursive https://github.com/ChampSim/ChampSim.git

WORKDIR /root/ChampSim

RUN vcpkg/bootstrap-vcpkg.sh
RUN vcpkg/vcpkg install

COPY generate_configs.py .
RUN python3 generate_configs.py

COPY ./compile_all.sh .
RUN chmod +x compile_all.sh
RUN ./compile_all.sh

COPY ./download_traces.sh .
RUN chmod +x download_traces.sh
RUN ./download_traces.sh

COPY ./run_all.sh .
RUN chmod +x run_all.sh
RUN ./run_all.sh
