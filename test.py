
import os
from time import sleep

def read_file_with_progress(filepath):
    # Get total number of lines for progress tracking
    with open(filepath, 'r') as file:
        total_lines = sum(1 for _ in file)

    print(f"Total lines: {total_lines}")
    read_lines = 0

    # Read file line by line and display progress
    with open(filepath, 'r') as file:
        for line in file:
            # Process each line (replace the sleep with your processing logic)
            #sleep(0.1)  # Simulating some processing delay
            read_lines += 1

            # Calculate and display progress
            progress = (read_lines / total_lines) * 100
            print(f"Progress: {progress:.2f}%", end="\r")
    
    print("\nProcessing completed.")

# Path to your file
file_path = "/home/beigi/temp/nginx/access.log.1"
read_file_with_progress(file_path)
