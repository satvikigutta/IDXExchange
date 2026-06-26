# Week 1 Monthly Dataset Aggregation

## Overview

This project contains a Python script for the Week 1 deliverable of the IDX Exchange Data Analyst Internship. The script combines monthly MLS listing and sold CSV files into two analysis-ready datasets.

The script reads all monthly `CRMLSListing` and `CRMLSSold` CSV files, concatenates them into combined datasets, filters both datasets to include only residential properties, and saves the final outputs as new CSV files.

## Purpose

The goal of this script is to prepare MLS data for future analysis by combining individual monthly files into larger datasets that span multiple months. This allows for trend analysis over time using residential property data.

## Files Included

- `week1 deliverable.py` — Python script that performs the monthly dataset aggregation
- `README.md` — Project description and usage instructions

## What the Script Does

The script:

1. Locates all monthly sold CSV files with the prefix `CRMLSSold`
2. Locates all monthly listing CSV files with the prefix `CRMLSListing`
3. Reads each CSV file into a pandas DataFrame
4. Prints row counts for each monthly file before concatenation
5. Combines all sold files into one sold dataset
6. Combines all listing files into one listing dataset
7. Filters both datasets to `PropertyType == "Residential"`
8. Prints row counts before and after filtering
9. Saves the final combined residential datasets as new CSV files

## Output Files

The script creates two new CSV files:

- `combined_sold_residential.csv`
- `combined_listing_residential.csv`

These output files are not included in this repository because the MLS data is confidential.

## Requirements

This script requires Python and pandas.

Install pandas with:

```bash
pip install pandas
