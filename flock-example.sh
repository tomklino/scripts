#!/bin/bash

flock -n /tmp/$(basename $0) -c 'echo "doing something long" && sleep 10 && echo "done"'
