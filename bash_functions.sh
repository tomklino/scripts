#!/bin/bash

function setWindowTitle() {
  PROMPT_COMMAND="echo -ne \"\033]0;$1\007\"";
}

function makeqr() {
  f=$(mktemp);
  qrencode $@ -o $f;
  eog $f 2>&1 1>/dev/null &
}

