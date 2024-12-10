# Define a function to read and store file content
def read_file_once(file_path):
    # Static variable to store the file content
    if not hasattr(read_file_once, "_file_content"):
        try:
            with open(file_path, "r") as file:
                # Read and store the file content
                read_file_once._file_content = file.read()
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            read_file_once._file_content = None
    return read_file_once._file_content

# Usage example
file_path = "/home/beigi/temp/nginx/access.log.1"

# First call reads and stores the content
file_content = read_file_once(file_path)
#print("First read:", file_content)

# Subsequent calls reuse the stored content
file_content_again = read_file_once(file_path)
print("Second read (reused):", file_content_again)
