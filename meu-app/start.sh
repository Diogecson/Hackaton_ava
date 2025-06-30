#!/bin/bash
export PYTHONUNBUFFERED=true

# Instalar o Chrome headless
apt-get update && apt-get install -y wget unzip curl
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb || true

# Rodar o app
python3 main.py
