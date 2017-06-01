#!/bin/bash

clearvars() { fqdn=""; ipaddress="";}

#echo $1

cat $1 | sed -r 's/^[ \t]+/---/' | while IFS= read -r line; do
  if [[ $line ]] ; then
    if [[ $line =~ ^--- ]]; then
      ipaddress=$(sed -r 's/^---macaddress:[^0-9a-fA-F]*([0-9a-fA-F\:]+).*$/\1/' <<< ${line});
    else
      fqdn=$(sed -r 's/^([^\:]+)\:/\1/' <<< $line)
    fi
  else
    #line is empty, print what you've got and clear vars
    printf "%s,%s\n" "$fqdn" "$ipaddress";
    clearvars;
  fi
done

