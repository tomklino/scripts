#!/binbash

resultsDir="scan-results";
mkdir $resultsDir;

tar xf server-to-scan.tar.gz
for ip in $(ls servers-to-scan-nmap-formatted.d); do
  PORTS=$(cat servers-to-scan-nmap-formatted.d/$ip);
  if [[ $PORTS ]]; then
    nmap $ip -p$PORTS -Pn > $resultsDir/$ip-results ;
  fi;
done

tar czf $resultsDir.tar.gz $resultsDir

rm -R $resultsDir
rm -R servers-to-scan-nmap-formatted.d

