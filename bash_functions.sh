#!/bin/bash

function setWindowTitle() {
  PROMPT_COMMAND="echo -ne \"\033]0;$1\007\"";
}
