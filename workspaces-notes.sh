CONF_FILE="${HOME}/.workspace-notes.conf"
NUM_OF_WORKSPACES=4 # default. will be overwritten by the value in conf_file
WINDOW_TITLE="Workspaces"

### Loading conf ###
if [[ ! -e "$CONF_FILE" ]]; then
  echo "no path defined for workspace notes working directory. type full path beginning with '/' or relative to home dir without '/':"
  read WORKING_DIR
  if [ "${WORKING_DIR:0:1}" != "/" ]; then
    WORKING_DIR="\${HOME}/$WORKING_DIR"
  fi
  echo "WORKING_DIR=${WORKING_DIR}" > $CONF_FILE
fi

source $CONF_FILE

### Creating Monthly Dir ###
MONTH=$(date +%B | awk '{print tolower($0)}')
cd $WORKING_DIR || (echo "could not cd into $WORKING_DIR" && exit)
if [[ ! -d ${MONTH}.d ]]; then
  mkdir ${MONTH}.d
fi

cd ${MONTH}.d || (echo "could not use ${MONTH}.d as a direcotry" && exit)
MONTHLY_FILE="$(date +%B-%Y).md"
touch $MONTHLY_FILE

### Creating Daily Files ###
DATE=$(date +%F)
if [[ ! -d workspaces-$DATE ]]; then
  mkdir workspaces-$DATE
fi

(cd $HOME; ln -f -s ${WORKING_DIR}/${MONTH}.d/workspaces-${DATE} daily-notes)

cd workspaces-$DATE

NUM_OF_WORKSPACES=${1:-$NUM_OF_WORKSPACES}
for i in $(seq 1 $NUM_OF_WORKSPACES); do
    touch workspace-${i}.md;
done

echo -e '\033]2;'$WINDOW_TITLE'\007'

vim "+tabdo windo set tw=80" -o workspace-* ../${MONTHLY_FILE}

