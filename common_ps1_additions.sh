#!/bin/bash

export PS1_ADDITIONS+=('\[\033[31m\]$(git branch 2> /dev/null | grep -e ^* | sed -E "s/^\*\ (.+)$/\(\1\) /")')
export PS1_ADDITIONS+=('\[\033[36m\]$(kubectl config current-context 2>/dev/null | sed -E "s/^(.+)$/{\1} /")')

