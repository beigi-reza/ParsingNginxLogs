import re
from datetime import datetime

def read_log_from_end(file_path, target_date_str, date_format='%Y-%m-%d %H:%M:%S'):
    target_date = datetime.strptime(target_date_str, date_format)
    
    with open(file_path, 'rb') as f:
        # Move to the end of the file
        f.seek(0, 2)
        file_size = f.tell()
        buffer_size = 1024
        buffer = bytearray()
        
        position = file_size
        while position > 0:
            position -= buffer_size
            if position < 0:
                buffer_size += position
                position = 0
            
            f.seek(position)
            buffer = f.read(buffer_size) + buffer
            
            lines = buffer.split(b'\n')
            for line in reversed(lines):
                try:
                    log_date_str = line.decode('utf-8').split(' ')[0]  # Assuming the date is the first part of the log entry
                    log_date = datetime.strptime(log_date_str, date_format)
                    if log_date <= target_date:
                        print(log_date)
                        return [line.decode('utf-8') for line in reversed(lines) if line.decode('utf-8').split(' ')[0] <= target_date_str]
                except ValueError:
                    # Skip lines that don't match the date format
                    print("1")
                    continue

        return []

# Example usage
file_path = '/home/beigi/myApp/ParsingNginxLogs/SampleFile/access.log'
target_date_str = '2024-09-14 16:56:24'
log_entries = read_log_from_end(file_path, target_date_str)

for entry in log_entries:
    print(entry)
