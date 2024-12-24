import re

# Sample log line
log_line = 'nginx    | 10.100.52.254 - - [24/Dec/2024:11:26:04 +0330] "GET /img/media/products/rh-1277/catalog-638101606868747748.pdf HTTP/1.1" 200 169186 "-" "Screaming Frog SEO Spider/19.8" "213.61.45.115"'

# Regex pattern to extract the real IP (last IP in quotes)
real_ip_pattern = r'"(\d+\.\d+\.\d+\.\d+)"$'

# Search for the real IP
match = re.search(real_ip_pattern, log_line)

if match:
    real_ip = match.group(1)
    print("Real IP Address:", real_ip)
else:
    print("Real IP Address not found")
