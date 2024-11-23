#! /usr/bin/python3


import docker


# Initialize the Docker client
client = docker.from_env()

# Replace with the name or ID of your container
container_name = "nginx"

try:
    # Fetch the container object
    container = client.containers.get(container_name)
    
#    # Get logs (as a string)
#    logs = container.logs().decode("utf-8")
#    
#    print("Container Logs:")
#    logs = container.logs(tail=10)
#    print(logs)

    for log in container.logs(stream=True):
        print(log.decode("utf-8").strip())


    
except docker.errors.NotFound:
    print(f"Container '{container_name}' not found.")
except Exception as e:
    print(f"An error occurred: {e}")
