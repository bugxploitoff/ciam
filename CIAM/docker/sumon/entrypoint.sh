#!/bin/bash

# Start the SSH server
/usr/sbin/sshd

# Create a root user with a password
echo "root:1234" | chpasswd

# Start Shell In A Box in the background with authentication enabled
shellinaboxd -t -s "/:LOGIN" -b &

# Keep the container running
tail -f /dev/null
