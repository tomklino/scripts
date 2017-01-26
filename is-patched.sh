#!/bin/bash
input=$1
versionregex="3\.16\.39\-1|3\.2\.84\-1"
space="\t"
echo -e "fqdn patched?" | column -t -c2

while read line; do
  uname=$(ssh -n $line -o "ConnectTimeout 15" -o "StrictHostKeyChecking no" "uname -a")
  if [ "$(echo $uname | grep -E $versionregex | wc -l)" == "1" ]; then
    patched="YES";
  else
    patched="NO";
  fi
  echo -e "$line $patched" | column -t -c2
done < $input
