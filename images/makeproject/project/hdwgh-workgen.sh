#!/bin/bash


DIRECTORY="./hdwgh_data/"

# Loop through all files in the directory
for file in "$DIRECTORY"/*
do
  echo "$file"
  # Check if it is a file (not a directory)
  if [ -f "$file" ]; then
    ./bin/stage_file $file
    filename=$(basename "$file")
    echo "Staged file $filename"
    # Extract the filename without the path
    ./bin/create_work --appname hdwgh \
        --wu_template templates/hdwgh_in \
        --result_template templates/hdwgh_out \
        --priority 12000 \
        --min_quorum 2 \
        --credit 5000 \
        --delay_bound 1209600 \
        --command_line "-jar HDWGHSeedFinding-all.jar" \
        $filename
    
    echo "Created work for $filename"
  fi
done