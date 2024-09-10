import re
from collections import Counter

# Path to the Nginx access log file
log_file = '/home/beigi/myApp/ParsingNginxLogs/SampleFile/access.log'

# Regular expression to match the URL and status code from the log entry
log_pattern = re.compile(r'"GET\s(\/[^\s]*)\sHTTP/1\.\d"\s(\d{3})')

# List to store URLs with redirect status codes
redirects = []

# Read the log file and extract URLs with status codes
with open(log_file, 'r') as f:
    for line in f:
        match = log_pattern.search(line)
        if match:
            url = match.group(1)  # Extract the URL
            status_code = int(match.group(2))  # Extract the status code
            if status_code in [301, 302, 303, 307, 308]:  # Check for redirect status codes
                redirects.append(url)

# Count the occurrences of each URL that caused a redirect
redirect_counter = Counter(redirects)

# Display the top 10 URLs with the most redirects
for url, count in redirect_counter.most_common(10):
    print(f"{url}: {count} redirects")
