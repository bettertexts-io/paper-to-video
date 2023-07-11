#!/bin/bash

filename="2023-06-19-18-02-32.txt"
last_min=-1
last_hour=-1
line_number=0
last_engine=""
last_job_counter=""


while IFS= read -r line
do
  line_number=$((line_number+1))
  
  # Extract hour and minute from the timestamp
  hour=$(echo $line | cut -d' ' -f2 | cut -d':' -f1)
  minute=$(echo $line | cut -d' ' -f2 | cut -d':' -f2)
  engine=$(echo $line | grep -o 'Job engine: .*' | cut -d ' ' -f 3)
  if [ "$engine" != "" ]; then
      last_engine=$engine
  fi

  # Skip lines without a valid timestamp
  if ! [[ $hour =~ ^[0-9]+$ ]] || ! [[ $minute =~ ^[0-9]+$ ]]; then
    continue
  fi

  # Check if this is the first line with a valid timestamp
  if [ $last_min -eq -1 ]; then
    last_min=$minute
    last_hour=$hour
    continue
  fi
  
  # Handle hour changes
  if [ $hour -gt $last_hour ]; then
    minute=$((minute + 60))
  elif [ $hour -lt $last_hour ]; then
    # This handles day changes, but not year changes or month changes
    minute=$((minute + 1440))
  fi
  
  diff=$(($minute - $last_min))
  if [ $diff -gt 2 ]; then
      echo "Longer than 2min wait at line $line_number. Difference is $diff minutes."
  fi
  
  # Store the last minute (and potentially hour) for the next comparison
  last_min=$minute
  last_hour=$hour
done < "$filename"

echo "Last engine: $last_engine"
echo "Last job counter: $last_job_counter"