#!/bin/bash

set -e

if [ ! -f build/lab_06 ]; then
    echo "Executable not found. Running build.sh first..."
    ./build.sh
fi

./build/lab_06
