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

function browse-notes() {
    days=${1:-180}
  ( source ~/.workspace-notes.conf;
    cd ${WORKING_DIR} && \
        find -daystart -mtime -${days} -type f \
        \( -name '*.txt' -o -name '*.md' \) -printf "%T@ %p\n" |\
        sort -rn | awk '{print $2}' | xargs cat | less -X
  )
}

bug-notes () {
	(
		cd ~/notes && grep --color=auto -rI "^Bug: $1" | cut -d':' -f1 | xargs cat | less -KFX -X
	)
}

