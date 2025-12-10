#!/usr/bin/env bash
set -e  # Exit on error

# Directory where this script lives
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$ROOT_DIR/solver"

if [ "$1" == "compile" ]; then

    # Clone the solver repo
    if [ -d "$SRC_DIR" ]; then
        echo "Solver source already exists. Pulling latest changes..."
        git -C "$SRC_DIR" pull
    else
        echo "Cloning solver repository..."
        git clone https://github.com/tfolkersen/SEGClobber.git "$SRC_DIR"
    fi

    # Compile the solver
    echo "Compiling solver..."
    cd "$SRC_DIR/src"
    make clean
    make

    # Verify
    BINARY="$SRC_DIR/src/segclobber"
    if [ -f "$BINARY" ]; then
        echo "Solver successfully compiled and placed in $SRC_DIR/src"
    else
        echo "Compilation failed."
        BINARY="$ROOT_DIR/bin/segclobber"
        export SEGCOBBER_BINARY="$BINARY"
        exit 1
    fi

else

    BINARY="$ROOT_DIR/bin/segclobber"
    echo "Using existing solver binary at $BINARY"

fi

export SEGCOBBER_BINARY="$BINARY"
