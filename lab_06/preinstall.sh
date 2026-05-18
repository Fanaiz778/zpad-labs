#!/bin/bash

set -e

echo "Updating package list..."
sudo apt update

echo "Installing dependencies..."
sudo apt install -y build-essential cmake make g++ libopencv-dev

echo "Preinstall completed successfully."
