#!/bin/bash
input=$1
versionregex="3\.16\.39\-1|3\.2\.84\-1"
printf "%-65s %-4s \n" "fqdn" "patched?"

while read line; do
  dpkg=$(ssh -n $line -o "ConnectTimeout 15" -o "StrictHostKeyChecking no" "dpkg -l | grep linux-image")
  if [ "$(echo $dpkg | grep -E $versionregex | wc -l)" == "0" ]; then
    prepared="NO";
  else
    prepared="YES";
  fi
  printf "%-65s %-4s \n" "$line" "$prepared"
done < $input
