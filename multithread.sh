#!/bin/bash

[[ ! $1 || ! $2 || ! $3 ]] && echo "usage: $(basename $0) input_file num_of_threads cmd_on_each_file
note: remember to escape \$" && exit 1  

inputfile=$1
threads=$2
cmd=${@:3}

filename=$(basename $inputfile)
total_length=$(wc -l $inputfile | awk '{ print $1 }')
tempdir="/tmp/$filename.d"
if [[ ! -d $tempdir ]] ; then 
  mkdir $tempdir
fi

cp $inputfile $tempdir

lines=$(expr $total_length / $threads)

split $tempdir/$filename --lines $lines $tempdir/x 

for f in $(ls $tempdir | grep ^x[a-z][a-z]$); do
  sh -c "while read line; do $cmd \$line; done < $tempdir/$f 2>/tmp/errors & ";
done

