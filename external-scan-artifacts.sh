#!/bin/bash

if ! [[ $1 ]]; then
  echo "usage: $(basename $0) /path/to/filename/with/server-names"
  exit 1
fi

originDirectory=$(pwd)
workingDirectory="/tmp/esa"

mkdir $workingDirectory

while read line; do
  ip=$(dig +noall +answer +short $line @8.8.8.8);
  if [[ $ip ]]; then
    echo -n $line\ >> $workingDirectory/public-ips-to-scan ;
    echo $ip >> $workingDirectory/public-ips-to-scan ;
  fi
done < $1

mkdir $workingDirectory/servers-to-scan.d
while read line; do
  host=$(echo $line | awk '{print $1}');
  ip=$(echo $line | awk '{print $2}');
  if [[ $host && $ip ]]; then
    ssh -n $host -o "StrictHostKeyChecking no" "sudo netstat -tunap | grep LISTEN" >> $workingDirectory/servers-to-scan.d/$ip;
  fi
done < $workingDirectory/public-ips-to-scan

mkdir $workingDirectory/servers-to-scan-formatted.d
for ip in $(ls $workingDirectory/servers-to-scan.d); do
  cat $workingDirectory/servers-to-scan.d/$ip | awk '{print $4}' | sed -r 's/([0-9\.]+|\:\:)\:([0-9]+)/\2/' | sort | uniq > $workingDirectory/servers-to-scan-formatted.d/$ip;
done 

mkdir $workingDirectory/servers-to-scan-nmap-formatted.d
for ip in $(ls $workingDirectory/servers-to-scan-formatted.d); do
  PORTS="";
  while read port; do
    if [[ $PORTS ]]; then
      PORTS="$PORTS,$port";
    else
      PORTS="$port"
    fi
  done < $workingDirectory/servers-to-scan-formatted.d/$ip;
  echo $PORTS > $workingDirectory/servers-to-scan-nmap-formatted.d/$ip;
done

cd $workingDirectory
tar czvf server-to-scan.tar.gz servers-to-scan-nmap-formatted.d
mv server-to-scan.tar.gz $originDirectory
cd $originDirectory
rm -R $workingDirectory
