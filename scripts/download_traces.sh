#!/bin/bash

TRACE_DIR="./traces"
mkdir -p "$TRACE_DIR"

TRACES=(
  "429.mcf-22B.champsimtrace.xz"
  "456.hmmer-88B.champsimtrace.xz"
  "623.xalancbmk_s-10B.champsimtrace.xz"
)

# Base URL
BASE_URL="https://dpc3.compas.cs.stonybrook.edu/champsim-traces/speccpu"

# Download
for TRACE in "${TRACES[@]}"; do
    echo "Downloading $TRACE ..."
    aria2c -x 8 -s 8 "$BASE_URL/$TRACE" -d "$TRACE_DIR" --console-log-level=info
done

