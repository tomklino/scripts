function echo-red() {
  echo -e "\e[31m$1\e[0m";
}

function helmet() {
  cluster=$(kubectl config view --minify -o jsonpath={.clusters[].name});
  tls=$(echo -n "--tls --tls-cert $HOME/.helm/tls/$cluster/cert.pem --tls-key $HOME/.helm/tls/$cluster/key.pem");
  helm "$@" ${tls};
}

function bootstrap-helm() {
  if [ "$(kubectl config current-context)" != "minikube" ]; then
    echo-red "kube context is not minikube. refusing to continue.";
    return;
  fi
  kubectl -n kube-system create sa tiller
  kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount kube-system:tiller
  helm init --service-account tiller
}

function dockercfg-to-minikube() {
  if [ "$(kubectl config current-context)" != "minikube" ]; then
    echo-red "kube context is not minikube. refusing to continue.";
    return;
  fi
  source ${HOME}/.gitlab_config
  if [ -z "$gitlab_username" ] || [ -z "$gitlab_password" ]; then
    echo-red "gitlab credentials are not set in ${HOME}/.gitlab_config - terminating."
    return;
  fi
  kubectl create secret docker-registry gitlab-registry --docker-server=registry.dev.nvsrc.com --docker-username=${gitlab_username} --docker-password=${gitlab_password}
  kubectl patch sa default -p '{"imagePullSecrets": [{"name": "gitlab-registry"}]}'
}
