import os
import subprocess
import random
from function.jwt import decode
from blockchain.block.registerblock import Blockchain  # Import your Blockchain class

blockchain_data_dir = 'blockchain/data/'
blockchain_file = os.path.join(blockchain_data_dir, 'docker.json')

# Initialize the Blockchain instance
blockchain = Blockchain()

def container_exists(container_id):
    # Check if the directory for the container exists
    dockerfile_dir = f'docker/{container_id}'
    dockerfile_path = f'{dockerfile_dir}/Dockerfile'
    return os.path.exists(dockerfile_dir)

def generate_dockerfile(container_id, ostype, user, password, session):
    if not container_id or not ostype:
        return {'status': 400, 'message': 'container_id and ostype are required'}
    
    if container_exists(container_id):
        return {'status': 200, 'message': 'Container already initialized'}

    dockerfile_content = f'''
# Use an {ostype}-based image as the base
FROM {ostype}:latest

# Install required packages
RUN apt-get update && \\
    apt-get install -y dialog curl jq shellinabox

# Set a custom environment variable for a unique identifier
ENV CONTAINER_ID={container_id}

# Copy the entrypoint script to the container
COPY entrypoint.sh ./entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Set the entrypoint script as the default entrypoint
ENTRYPOINT ["/entrypoint.sh"]
'''

    # Define the path to save the Dockerfile
    dockerfile_dir = f'docker/{container_id}'
    dockerfile_path = f'{dockerfile_dir}/Dockerfile'
    
    # Create the directory if it doesn't exist
    os.makedirs(dockerfile_dir, exist_ok=True)

    # Save the Dockerfile content to a file
    with open(dockerfile_path, 'w') as dockerfile:
        dockerfile.write(dockerfile_content)

    # Create the entrypoint.sh script in the same folder
    entrypoint_content = f'''#!/bin/bash

# Start the SSH server
/usr/sbin/sshd

# Create a root user with a password
echo "root:{password}" | chpasswd

# Start Shell In A Box in the background with authentication enabled
shellinaboxd -t -s "/:LOGIN" -b &

# Keep the container running
tail -f /dev/null
'''

    entrypoint_path = f'{dockerfile_dir}/entrypoint.sh'
    with open(entrypoint_path, 'w') as entrypoint:
        entrypoint.write(entrypoint_content)

    return {'status': 200, 'message': 'Dockerfile and entrypoint.sh generated successfully', 'dockerfile_path': dockerfile_path}

def build_and_run_container(container_id, user, session, random_port):
    dockerfile_dir = f'docker/{container_id}'
    dockerfile_path = f'{dockerfile_dir}/Dockerfile'

    # Build the Docker image with a tag based on the container ID
    image_name = f'{user}'
    build_command = ['docker', 'build', '-t', image_name, dockerfile_dir]
    subprocess.run(build_command, check=True)

    # Generate a random port for Shell In A Box
    random_port = random.randint(49152, 65535)

    # Run the Docker container with a random port mapping for Shell In A Box
    run_command = ['docker', 'run', '-d', f'-p', f'{random_port}:4200', image_name]
    subprocess.run(run_command, check=True)
    decoded_payload = decode(session)
    email = decoded_payload['email']
    data = f"email: {email}, uuid: {user}, containerid: {container_id}, port: {random_port}"
    blockchain.mine_block(data)

    # Save the blockchain data to the JSON file
    blockchain.save_to_file(blockchain_file)

    return {'status': 200, 'message': 'Container built and started successfully', 'random_port': random_port}

def perform_addcontainer(container_id, ostype, user, password, session):
    if not container_id or not ostype or not session:
        return {'status': 400, 'message': 'container_id, ostype, and session are required'}

    if container_exists(container_id):
        return {'status': 200, 'message': 'Container already initialized'}

    result = generate_dockerfile(container_id, ostype, user, password, session)
    if result['status'] == 200:
        random_ports = random.randint(49152, 65535)
        random_port = build_and_run_container(container_id, user, session, random_ports)
        result['random_port'] = random_port

    return result
    print (result)

