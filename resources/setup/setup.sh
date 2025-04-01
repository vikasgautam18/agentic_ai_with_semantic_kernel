#!/bin/bash

apt-get update -y
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    unzip \
    jq \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r src/demos/requirements.txt