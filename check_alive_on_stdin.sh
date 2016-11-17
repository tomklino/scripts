#!/bin/bash

while read line; do 
  ping -c 2 $line | grep -A1 "ping statistics";
done
