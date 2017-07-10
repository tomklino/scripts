while read line; do
  ip=$(echo $line | cut -d "," -f1);
  ping $ip -c1 -W1 >/dev/null;
  if [[ $? == 0 ]]; then result="alive"; else result="probably dead"; fi;
  printf "%s,%s\n" "$result" "$line";
done;

