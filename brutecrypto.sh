#!/bin/bash

if [[ !( $1 && $2 ) ]]; then
  echo "usage: $(basename $0) filename maxkey"
  echo "maxkey needs to be a number"
  echo 'tip: use "notify-send $(usage syntax)" to get notified at the end'
fi

if [[ $2 =~ ^[0-9]+$ ]]; then
  from=0
  to=$2
else
  from=$(sed -r 's/([0-9]+)-.*/\1 /' <<< $2)
  to=$(sed -r 's/[0-9]+-([0-9]+)/\1/' <<< $2)
fi

echo >&2 "range is $from $to"

for k in $(seq $from $to); do
  if [[ $(expr $k % 5000) == 0 ]]; then
    >&2 echo -n "."
  fi
  export k;
  ccdecrypt -E k $1 2>/dev/null;
  if [[ $? == 0 ]]; then
    echo "it broke!"
    break;
  fi
done
if [[ $k == $2 ]]; then
  echo "it didnt break :-("
fi
