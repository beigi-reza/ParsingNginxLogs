#####   import re
#####   from collections import Counter
#####   
#####   # Path to the Nginx access log file
#####   log_file = '/home/beigi/myApp/ParsingNginxLogs/SampleFile/access.log'
#####   
#####   # Regular expression to match the URL and status code from the log entry
#####   log_pattern = re.compile(r'"GET\s(\/[^\s]*)\sHTTP/1\.\d"\s(\d{3})')
#####   
#####   # Dictionary to store the status codes and their counts
#####   status_code_counter = Counter()
#####   
#####   # Read the log file and extract URLs with status codes
#####   with open(log_file, 'r') as f:
#####       for line in f:
#####           match = log_pattern.search(line)
#####           if match:
#####               url = match.group(1)  # Extract the URL
#####               status_code = int(match.group(2))  # Extract the status code
#####               status_code_counter[status_code] += 1  # Increment the count for this status code
#####   
#####   # Display the count of each status code
#####   for status_code, count in status_code_counter.most_common():
#####       print(f"Status Code {status_code}: {count} occurrences")

import re

# Sample Nginx log entry
log_entry = '127.0.0.1 - - [10/Sep/2024:12:34:56 +0000] "GET / HTTP/1.1" 200 612 "-" "Mozilla/5.0"'

# Regex pattern to capture the date and time
pattern = r'\[(\d{2})/(\w{3})/(\d{4}):(\d{2}):(\d{2}):(\d{2}) [+-]\d{4}\]'

# Find the date and time in the log entry
match = re.search(pattern, log_entry)

if match:
    day, month, year, hour, minute, second = match.groups()
    print(f"Date: {day} {month} {year}")
    print(f"Time: {hour}:{minute}:{second}")
    
    print(f"{day} {month} {year} / {hour}:{minute}:{second}")
else:
    print("No match found.")
