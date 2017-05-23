#!/bin/bash

#usage external-scan-artifacts.sh /path/to/filename/with/server-names

hostName() { awk '{print $1}' <<< $1 }
ipAddress() { awk '{print $2}' <<< $1 }

workingDirectory="/tmp/esa"

mkdir $workingDirectory/public-ips-to-scan
while read line; do echo -n $line\ >> $workingDirectory/public-ips-to-scan ;dig +noall +answer +short $line @8.8.8.8 >> $workingDirectory/public-ips-to-scan ; done < $1

mkdir $workingDirectory/servers-to-scan.d
while read line; do
  host=$(hostName "$line");
  ip=$(ipAddress "$line");
  ssh -n $host -o "StrictHostKeyChecking no" "sudo netstat -tunap | grep LISTEN" >> $workingDirectory/servers-to-scan.d/$ip;
done < $workingDirectory/public-ips-to-scan

mkdir $workingDirectory/servers-to-scan-formatted.d
for ip in $(ls $workingDirectory/servers-to-scan.d); do
  cat $workingDirectory/servers-to-scan.d/$ip | awk '{print $4}' | sed -r 's/([0-9\.]+|\:\:)\:([0-9]+)/\2/' | sort | uniq > $workingDirectory/servers-to-scan-formatted.d/$ip;
done 

mkdir $workingDirectory/servers-to-scan-nmap-formatted.d
for ip in $(ls $workingDirectory/servers-to-scan-formatted.d); do
  PORTS="80";
  while read port;
    do PORTS="$PORTS,$port";
  done < $workingDirectory/servers-to-scan-formatted.d/$ip;
  echo $PORTS > $workingDirectory/servers-to-scan-nmap-formatted.d/$ip;
done

cd $workingDirectory
tar czvf server-to-scan.tar.gz servers-to-scan-nmap-formatted.d
