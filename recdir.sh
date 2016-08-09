#!/bin/bash
#recdir: listens with nc to a directory structure being sent with sendir.ssh
#        and extracts it to the current working directory
#usage: recdir [<port>]
#port defaults to 3000

if [[ $(echo $3 | egrep "^[0-9]+$" | wc -l) = 0 ]]; then
  $3=3000
fi

nc -l -p 3000 | tar zx
