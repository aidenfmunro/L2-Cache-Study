#!/bin/bash

BIN_DIR="./bin"
TRACE_DIR="./traces"
RESULT_DIR="./results"
CONFIGS_DIR="./configs"
WARMUP=50000000
SIM=100000000

mkdir -p "$RESULT_DIR"

export BIN_DIR TRACE_DIR RESULT_DIR WARMUP SIM

for BIN_PATH in "$BIN_DIR/"*; do
  BIN_NAME=$(basename "$BIN_PATH")

  for TRACE_PATH in "$TRACE_DIR/"*.champsimtrace.xz; do
    TRACE_NAME=$(basename "$TRACE_PATH" .champsimtrace.xz)

    OUTFILE="${RESULT_DIR}/${BIN_NAME}_${TRACE_NAME}.txt"

    echo "Запуск $CONFIG на $TRACE_PATH ..."
    "$BIN_PATH" --warmup-instructions $WARMUP --simulation-instructions $SIM "$TRACE_PATH" > "$OUTFILE" &
  done
done

wait

