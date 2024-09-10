import pandas as pd
import re

# Path to the Nginx access log file
log_file = 'access.log'

# Regular expression to match the URL from the log entry
url_pattern = re.compile(r'"GET\s(\/[^\s]*)')

# Create an empty list to store log data
log_data = []

# Read the log file and extract URLs
with open(log_file, 'r') as f:
    for line in f:
        match = url_pattern.search(line)
        if match:
            url = match.group(1)  # Get the matched URL
            log_data.append(url)

# Create a DataFrame from the extracted URLs
df = pd.DataFrame(log_data, columns=['URL'])

# Count the occurrences of each URL
url_counts = df['URL'].value_counts().reset_index()
url_counts.columns = ['URL', 'Count']

# Display the top 10 most common URLs
print(url_counts.head(10))
