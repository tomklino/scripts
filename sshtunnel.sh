#!/bin/bash
#creates a ssh tunnel and moves to background

#if not enough attributes supplied, or supplied incorrectly, show usage
#TODO: add an if statement to check the above
echo "usage:\n"
echo "sshtunnel.sh <connection> <local-port> <remote-port> [<goto-address>]\n"
echo "<connection> is how to connect to the ssh. Example: 'root@192.168.0.1'\n"
echo "<local-port> is the port on the machine, <remote-port> is the port on the ssh tunnel will go to\n"
echo "<goto-address> is the address the ssh tunnel leads to. Default to 127.0.0.1 (stays on the remote machine)\n"

ssh $1 -N -L $2:127.0.0.1:$3
