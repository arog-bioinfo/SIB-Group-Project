#!/bin/bash
set -e

# Unzip packages (idempotent: overwrite is fine)
unzip -o data/raw/delta.zip   -d data/delta
unzip -o data/raw/omicron.zip -d data/omicron

# Create TSV metadata tables from NCBI packages
dataformat tsv virus-genome \
  --package data/raw/delta.zip \
  --fields accession,virus-name,geo-location,isolate-collection-date \
  > data/delta/delta_meta.tsv

dataformat tsv virus-genome \
  --package data/raw/omicron.zip \
  --fields accession,virus-name,geo-location,isolate-collection-date \
  > data/omicron/omicron_meta.tsv
