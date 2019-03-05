#!/bin/bash
cmd="$@"

echo "$cmd"
function execute() {
  $($@)
  return $?
}

until execute "$cmd"; do
  echo -n ".";
  sleep 1;
done;

echo '!'

