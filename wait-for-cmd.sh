#!/bin/bash
usage() {
  exitcode="$1"
  cat << USAGE >&2
Usage:
  $0 [-r retries] [-t timeout] -- command args
  -t TIMEOUT | --timeout=timeout      Time to wait between retries
  -t RETRIES | --retries=retries      Max amout of retries after which will exit with failure
  -- COMMAND ARGS                     Command with args to test
USAGE
  exit "$exitcode"
}

while [ $# -gt 0 ]
do
  case "$1" in
    -t)
    TIMEOUT="$2"
    if [ "$TIMEOUT" = "" ]; then break; fi
    shift 2
    ;;
    --timeout=*)
    TIMEOUT="${1#*=}"
    shift 1
    ;;
    -r)
    RETRIES="$2"
    if [ "$RETRIES" = "" ]; then break; fi
    shift 2
    ;;
    --retries=*)
    RETRIES="${1#*=}"
    shift 1
    ;;
    --)
    shift
    break
    ;;
    --help)
    usage 0
    ;;
    *)
    echo "Unknown argument: $1"
    usage 1
    ;;
  esac
done

# Preserve quotes arround quoted arguments
cmd=''
for i in "$@"; do
  case "$i" in
      *\'*)
          i=`printf "%s" "$i" | sed "s/'/'\"'\"'/g"`
          ;;
      *) : ;;
  esac
  cmd="$cmd '$i'"
done

if [[ -z "$TIMEOUT" ]]; then TIMEOUT=1; fi
if [[ -z "$cmd" ]]; then
  usage 1;
fi

echo "waiting for ${cmd}"
function execute() {
  (bash -c "$@ > /dev/null 2>&1");
  code=$?;
  return $code;
}

FAILS=0
until execute "$cmd"; do
  FAILS=$((FAILS+1))
  if [[ ! -z ${RETRIES} ]] && [[ ${FAILS} == ${RETRIES} ]]; then
    echo "maximum amout of retries (${RETRIES}) exceeded";
    exit 1;
  fi
  echo -n ".";
  sleep $TIMEOUT;
done;

echo '!'
