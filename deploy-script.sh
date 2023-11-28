#!/bin/bash


# Add the Deadsnakes PPA
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update


# Install a specific Python version, e.g., Python 3.9
sudo apt install python3.9

# Upgrade pip for the installed Python version
python3.9 -m pip install --upgrade pip

# Install requirements using the newly installed Python version
python3.9 -m pip install -r requirements.txt