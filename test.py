import re
from collections import OrderedDict,Counter

def order_dict_by_value(d):
    """Orders a dictionary by its values in descending order.

    Args:
        d: The dictionary to be ordered.

    Returns:
        An OrderedDict with the same keys and values as the input dictionary,
        but ordered by value in descending order.
    """

    return OrderedDict(sorted(d.items(), key=lambda item: item[1], reverse=True))


# Define the log format regex
log_format = r'(?P<ip>[\d\.]+) - - \[(?P<time>[^\]]+)\] "(?P<method>[A-Z]+) (?P<url>[^ ]+) HTTP/[0-9.]+" (?P<status>\d{3}) (?P<size>\d+) "(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'

# Path to your Nginx log file
log_file_path = "/home/beigi/temp/nginx/access.log.1"

# Counter to store occurrences of referers
referer_counter = Counter()

# Parse the log file
with open(log_file_path, 'r') as log_file:
    for line in log_file:
        match = re.match(log_format, line)
        if match:
            # Extract the referer field
            referer = match.group('referer')
            # Increment count for the referer
            referer_counter[referer] += 1





# Print the results
print("Referer counts:")
ordereeee = order_dict_by_value(referer_counter)

for _ in ordereeee:
    print(f"{_}: {ordereeee[_]}")    
