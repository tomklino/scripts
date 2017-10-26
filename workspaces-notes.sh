WORKING_DIR=/home/tomk/Documents/Wix
NUM_OF_WORKSPACES=4
DATE=$(date +%F)
MONTH=$(date +%B | awk '{print tolower($0)}')

cd $WORKING_DIR
if [[ ! -d ${MONTH}.d ]]; then
  mkdir ${MONTH}.d
fi

cd ${MONTH}.d || (echo "could not use ${MONTH}.d as a direcotry" && exit)

if [[ ! -d workspaces-$DATE ]]; then
  mkdir workspaces-$DATE
fi

cd workspaces-$DATE

for i in $(seq 1 4); do touch workspace-$i; done

vim -O *
