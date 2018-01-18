#!/bin/bash

hours=$1
pname=$2

echo "will kill $pname in $hours hours"

for i in $(seq 1 $hours); do
  let "remaining = $hours - $i + 1"
  notify-send -t 60000 "$remaining hours remaining"
  sleep 3600
done

notify-send -t 60000 "two minutes warning"
sleep 120
pkill $pname
