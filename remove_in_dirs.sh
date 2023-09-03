#!/bin/bash

# Check if the correct number of arguments are passed
if [ "$#" -ne 2 ]; then
    echo "You must enter exactly 2 command line arguments"
    exit 1
fi

# Assign the arguments to variables
base_path=$1
file_prefix=$2

# Use find command to locate and delete the files
find $base_path -type f -name "$file_prefix*" -exec rm -f {} \;
