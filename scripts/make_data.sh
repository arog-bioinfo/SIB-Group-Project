#!/bin/bash
set -e

mkdir -p data/raw

download_if_missing () {
  local lineage=$1
  local filename=$2
  if [ -f "data/raw/${filename}.zip" ]; then
    echo "Skipping ${filename}: data/raw/${filename}.zip already exists"
  else
    echo "Downloading ${filename}..."
    datasets download virus genome taxon sars-cov-2 \
      --host human \
      --lineage "${lineage}" \
      --complete-only \
      --fast-zip-validation \
      --filename "data/raw/${filename}.zip"
  fi
}

# 1) B.1 (ancestral-like)
download_if_missing "B.1" "b1"

# 2) XBB.1.5 (Omicron subvariant)
download_if_missing "XBB.1.5" "xbb15"

# 3) Beta (B.1.351)
download_if_missing "B.1.351" "beta"

# 4) Delta (B.1.617.2)
download_if_missing "B.1.617.2" "delta"

# 5) Omicron BA.1
download_if_missing "BA.1" "omicron_ba1"

# 6) Omicron BA.2
download_if_missing "BA.2" "ba2"