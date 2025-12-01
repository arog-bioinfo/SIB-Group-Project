#!/bin/bash
set -e

mkdir -p data/raw

# Delta (B.1.617.2)
datasets download virus genome taxon sars-cov-2 \
  --host human \
  --lineage B.1.617.2 \
  --released-after 2021-06-01 \
  --complete-only \
  --fast-zip-validation \
  --filename data/raw/delta.zip

# Omicron BA.1
datasets download virus genome taxon sars-cov-2 \
  --host human \
  --lineage BA.1 \
  --released-after 2021-12-01 \
  --complete-only \
  --fast-zip-validation \
  --filename data/raw/omicron.zip
