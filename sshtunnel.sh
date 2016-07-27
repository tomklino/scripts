#!/bin/bash
#creates a ssh tunnel and moves to background

#if not enough attributes supplied, or supplied incorrectly, show usage
if [[ $(echo $1 | egrep "^[0-9a-zA-Z]+@[0-9a-zA-Z\\.]+$" | wc -l) = 0 ]] || [[ $(echo $2 | egrep "^[0-9]+$" | wc -l) = 0 ]] || [[ $(echo $3 | egrep "^[0-9]+$" | wc -l) = 0 ]] ; then
	echo "usage:"
	echo "sshtunnel.sh <connection> <local-port> <remote-port> [<goto-address>]"
	echo "<connection> is how to connect to the ssh. Example: 'root@192.168.0.1'"
	echo "<local-port> is the port on the machine, <remote-port> is the port on the ssh tunnel will go to"
	echo "<goto-address> is the address the ssh tunnel leads to. Default to 127.0.0.1 (stays on the remote machine)"
else
	ssh $1 -N -L $2:127.0.0.1:$3
fi
