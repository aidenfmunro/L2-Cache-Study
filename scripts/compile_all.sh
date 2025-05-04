#!/bin/bash

set -e  # Stop on error

CONFIG_DIR="configs"
BIN_DIR="bin"

mkdir -p "$BIN_DIR"

for config_path in "$CONFIG_DIR"/*.json; do
    config_file=$(basename "$config_path")
    name="${config_file%.json}"  # strip .json

    echo "🔧 Building config: $config_file -> $BIN_DIR/champsim_$name"

    ./config.sh "$config_path"
    make -j$(nproc)
    mv "$BIN_DIR/champsim" "$BIN_DIR/champsim_$name"
done

echo "✅ All configurations compiled and saved in '$BIN_DIR/'"

