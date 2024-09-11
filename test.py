import re
from collections import Counter


Agent_counter = Counter()
# Function to extract user-agent browser info
def extract_browser(user_agent):
    # Simple regex to match popular browsers like Chrome, Firefox, Safari, etc.
    browser_regex = r"(Chrome|Firefox|Safari|Opera|Edge|Trident|Googlebot|facebookexternalhit|meta-externalagent|curl|Dalvik|WordPress)"
    match = re.search(browser_regex, user_agent)
    if match:
        return match.group(1)
    Agent_counter[user_agent] +=1
    return "Unknown"

# Parse the nginx access log
def parse_nginx_log(file_path):
    # Initialize a counter to count browsers
    browser_counter = Counter()

    # Open the access log
    with open(file_path, 'r') as file:
        for line in file:
            # Extract the user-agent part (between the quotes after the last '-')
            user_agent = line.split('"')[-4]
            browser = extract_browser(user_agent)
            browser_counter[browser] += 1
    
    return browser_counter

# Path to the nginx access log
log_file_path = "/home/beigi/myApp/ParsingNginxLogs/SampleFile/access.log"

# Get the browser count
browser_count = parse_nginx_log(log_file_path)

# Display the results

for _ in Agent_counter:
    print (f"{_}: {Agent_counter[_]}")
for browser, count in browser_count.items():
    print(f"{browser}: {count}")
