#!/bin/bash

set -e

echo "Updating package list..."
sudo apt update

echo "Installing dependencies..."
sudo apt install -y build-essential cmake make g++ libopencv-dev wget

mkdir -p models

echo "Downloading face detector architecture..."
wget -O models/deploy.prototxt \
https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt

echo "Downloading face detector weights..."
wget -O models/res10_300x300_ssd_iter_140000.caffemodel \
https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel

echo "Preinstall completed successfully."
