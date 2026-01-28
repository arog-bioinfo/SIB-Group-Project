#!/bin/bash
set -e

# Variants and nice names
variants=("b1" "beta" "delta" "omicron_ba1" "ba2" "xbb15")

# Unzip all NCBI packages into separate folders
for v in "${variants[@]}"; do
  mkdir -p "data/${v}"
  unzip -o "data/raw/${v}.zip" -d "data/${v}"
done

# Create TSV metadata tables using dataformat
for v in "${variants[@]}"; do
  dataformat tsv virus-genome \
    --inputfile "data/${v}/ncbi_dataset/data/data_report.jsonl" \
    --fields accession,virus-name,geo-location,isolate-collection-date \
    > "data/${v}/${v}_meta.tsv"
done


