#!/bin/bash

while read line; do
  ip=$(cut -d',' -f1 <<< $line)
  ipClue=$(awk -F'.' '{print $3"."$4}' <<< $ip)
  env=$(cut -d',' -f2 <<< $line)
  if [ "$env" = "tampa" ]; then
    envClue="production_tam";
  elif [ "$env" = "austin" ]; then
    envClue="production_aus";
  else
    envClue=""
  fi

  if [[ $(grep -E "^[0-9]+\.[0-9]+$" <<< $ipClue) ]] && [[ ! -z $envClue ]]; then
    valid=true
  else
    valid=false
  fi

  if $valid; then
    chefName=$(knife search node "ipaddress:*${ipClue} AND chef_environment:${envClue}" -i 2>/dev/null)
  else
    chefName=""
  fi
  
  printf "%s,%s\n" "$line" "$chefName"
done < $1
