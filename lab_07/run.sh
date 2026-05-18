#!/bin/bash

set -e

if [ ! -f build/lab_07 ]; then
    echo "Executable not found. Running build.sh first..."
    ./build.sh
fi

./build/lab_07
