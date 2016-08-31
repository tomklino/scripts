#!/bin/bash

if [[ ! $1 ]]; then
  echo "$0: must include at least one argument"
  exit 1;
fi

sed "s/$1/$2/"
