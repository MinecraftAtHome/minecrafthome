#!/bin/bash


DIRECTORY="./shbookfinder_data/"

# Loop through all files in the directory
for file in "$DIRECTORY"/*
do
  echo "$file"
  # Check if it is a file (not a directory)
  if [ -f "$file" ]; then
    ./bin/stage_file --copy "$file"
    filename=$(basename "$file")
    echo "Staged file $filename"
    # Extract the filename without the path
    ./bin/create_work --appname shbookfinder \
        --wu_template templates/shbookfinder_in \
        --result_template templates/shbookfinder_out \
        --priority 12000 \
        --min_quorum 2 \
        --credit 5000 \
        "$filename"
    
    echo "Created work for $filename"
  fi
done