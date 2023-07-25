
spin-help() {
    echo "### Waze Spinnaker CLI Help ###"
    echo "spin-iap      -  Reload IAP token for Spinnaker CLI (roer/curl)"
    echo "spin-default  -  Fixes the kubectl default namespace for spinnaker context"
    echo "spin-curl     -  Allows running authenticated curl commands to Spinnaker gate endpoint (need to run spin-iap first). First parameter is the api rest url (without the hostname). Other parameters can be chained for curl"
    echo "spin-swagger  -  Opens the gate swagger UI in the browser, to view which API endpoints exists, and which parameters they get"
    echo "spin-kill-execute - Kills a task which is hang and can't be stopped from UI. Get's parameter of EXECUTION_ID"
}

spin-curl(){
    curl -s -H "Authorization: Bearer $SPINNAKER_IAP_TOKEN" $SPINNAKER_API/$@
}

spin-swagger(){
    echo $SPINNAKER_API/swagger-ui.html
}

spin-kill-execute(){
    if [ -z "$1" ]
    then
        echo "You must provide an Execution ID as parameter"
    else
      kubectl config use-context gke_waze-ci_europe-west1_spinnaker-prod1
      EXEC_ID=$1
      ORCA=$(kubectl get pods -n spinnaker | grep spin-orca | head -1 | awk '{print $1}')
      kubectl -n spinnaker port-forward $ORCA 8083:8083 &
      while :
      do
          echo "Trying to port forward to orca..."
          nc -z localhost 8083 2> /dev/null
          if [ "$?" -eq "0" ]
            then break
          fi
          sleep 2
      done
      echo "Port forwarding to ORCA succeeded!"
      FG_ID=$!
      curl -XPUT "http://localhost:8083/admin/forceCancelExecution?executionId=$EXEC_ID&executionType=PIPELINE" -vvv
      kill $FG_ID
    fi
}

