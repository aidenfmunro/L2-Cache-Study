#!/bin/bash

TRACE_DIR="./traces"
mkdir -p "$TRACE_DIR"

TRACES=(
  "435.gromacs-228B.champsimtrace.xz"
  "649.fotonik3d_s-10881B.champsimtrace.xz"
  "453.povray-887B.champsimtrace.xz"
)

# Base URL
BASE_URL="https://dpc3.compas.cs.stonybrook.edu/champsim-traces/speccpu"

# Download
for TRACE in "${TRACES[@]}"; do
    echo "Downloading $TRACE ..."
    aria2c -x 8 -s 8 "$BASE_URL/$TRACE" -d "$TRACE_DIR" --console-log-level=info
done

