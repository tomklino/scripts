#!/bin/bash
#sendir: compresses and sends an entire directory structure over the network
#usage: sendir <dirname> <ipaddress> [<port>]
#port defaults to 3000

if [[ $(echo $3 | egrep "^[0-9]+$" | wc -l) = 0 ]]; then
  $3=3000
fi

tar cz $1 | nc $2 $3
