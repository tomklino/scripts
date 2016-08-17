#!/bin/bash

[[ ! $1 ]] && echo "usage: findbyname.sh <name>" && exit;

find $PWD -name "$1"
