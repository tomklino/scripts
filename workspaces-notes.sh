CONF_FILE="${HOME}/.workspace-notes.conf"
NUM_OF_WORKSPACES=4
DATE=$(date +%F)
MONTH=$(date +%B | awk '{print tolower($0)}')
WINDOW_TITLE="Workspaces"

if [[ ! -e "$CONF_FILE" ]]; then
  echo "no path defined for workspace notes working directory. type full path beginning with '/' or relative to home dir without '/':"
  read WORKING_DIR
  if [ "${WORKING_DIR:0:1}" != "/" ]; then
    WORKING_DIR="\${HOME}/$WORKING_DIR"
  fi
  echo "WORKING_DIR=${WORKING_DIR}" > $CONF_FILE
fi

source $CONF_FILE

cd $WORKING_DIR || (echo "could not cd into $WORKING_DIR" && exit)
if [[ ! -d ${MONTH}.d ]]; then
  mkdir ${MONTH}.d
fi

cd ${MONTH}.d || (echo "could not use ${MONTH}.d as a direcotry" && exit)

if [[ ! -d workspaces-$DATE ]]; then
  mkdir workspaces-$DATE
fi

cd workspaces-$DATE

for i in $(seq 1 $NUM_OF_WORKSPACES); do touch workspace-${i}.txt; done
touch general.txt;

echo -e '\033]2;'$WINDOW_TITLE'\007'

vim -o workspace-* general.txt

