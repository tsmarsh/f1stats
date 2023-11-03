#!/bin/bash

# Change to your actual directory where the CSV files are located
CSV_DIR="./data"
DB_NAME="f1.db"

# Start with an empty list of arguments
ARGS=""

# Loop over the CSV files and add them to the arguments list
for csv in $CSV_DIR/*.csv; do
  ARGS="$ARGS -f \"$csv\""
done

# Now run csv-to-sqlite with all the arguments
eval "csv-to-sqlite $ARGS -o $DB_NAME"
