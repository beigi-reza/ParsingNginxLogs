import requests
import json

# Docker socket URL for local communication
#DOCKER_API_URL = "http+unix://%2Fvar%2Frun%2Fdocker.sock/v1.41/containers/json"
DOCKER_API_URL = "http://10.1.8.181:2375/v1.41/containers/json"

# If using TCP/IP (remote communication), replace with your Docker host and port
# DOCKER_API_URL = "http://<docker-host-ip>:2375/v1.41/containers/json"

def list_docker_containers(api_url):
    try:
        # Request the list of containers
        response = requests.get(api_url)
        
        # Check for errors
        if response.status_code == 200:
            containers = response.json()
            return containers
        else:
            print(f"Error: Unable to fetch containers (Status Code: {response.status_code})")
            print(response.text)
            return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

# Fetch container list
containers = list_docker_containers(DOCKER_API_URL)


with open("data.json", "w") as json_file:
    json.dump(containers, json_file)
# Print the results
if containers:
    for container in containers:
        print(f"ID: {container['Id'][:12]}, Names: {container['Names']}, Image: {container['Image']}")
else:
    print("No containers found or unable to connect to the Docker API.")
