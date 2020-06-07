#!/bin/bash

function summarize-week-notes() {
  ( source ~/.workspace-notes.conf;
    cd ${WORKING_DIR};
    find -type f -mtime -7 -not -size 0 \
    -printf "%T@ %Tc '%p'\n" | sort -n |\
     sed -nE "/txt'$/s/.*'(.*txt)'/\1/p" |\
    while read f; do echo "------${f}-------"; cat ${f}; done |\
    less -X
  )
}

