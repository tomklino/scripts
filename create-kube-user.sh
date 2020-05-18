username=$1
namespace=$2

api_server_address="https://api.dev.nvsrc.com"        # "https://134.209.251.139:6443"
ca_file="/home/tomk/nuvo-kubernetes/ca.crt"           # "/home/tomk/workspace/kubernetes-thw/users/ca.crt"
admin_kubeconfig="/home/tomk/.kubeconfigs/dev"        # "/home/tomk/workspace/kubernetes-thw/kubeconfigs/cluster-a-admin"

cd ~/nuvo-kubernetes/dev/users

echo "Creating workdir..."
mkdir $username
cd $username

echo "Creating cnf file for ${username}"
cat > ${username}.cnf <<EOF
[ req ]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn

[ dn ]
CN = $username
O = regulars

[ v3_ext ]
authorityKeyIdentifier=keyid,issuer:always
basicContraints=CA:FALSE
keyUsage=keyEnchipherment,dataEncipherment
extendedKeyUsage=serverAuth,clientAuth
EOF

echo "generating key and csr for ${username}"
openssl genrsa -out ${username}.key 2048
openssl req -config ./${username}.cnf -new -key ${username}.key -nodes -out ${username}.csr

echo "generating csr yaml for ${username}"
cat > ${username}-csr.yaml <<EOF
apiVersion: certificates.k8s.io/v1beta1
kind: CertificateSigningRequest
metadata:
  name: ${username}-csr
spec:
  request: $(cat ${username}.csr | base64 | tr -d '\n')
  usages:
  - digital signature
  - key encipherment
  - server auth
  - client auth
EOF

echo "Sending csr to be signed on the api server..."
kubectl --kubeconfig=${admin_kubeconfig} apply -f ${username}-csr.yaml
echo "done"

echo "Approving csr for ${username}..."
kubectl --kubeconfig=${admin_kubeconfig} certificate approve ${username}-csr
echo "done"

echo "Getting the crt..."
kubectl --kubeconfig=${admin_kubeconfig} get certificatesigningrequests.certificates.k8s.io ${username}-csr -ojsonpath='{.status.certificate}' | base64 -d > ${username}.crt
echo "done"

echo "Creating kubeconfig for ${username}"
kubectl --kubeconfig=${username}-kubeconfig config set-cluster cluster-a --server="${api_server_address}" --certificate-authority=${ca_file} --embed-certs
kubectl --kubeconfig=${username}-kubeconfig config set-credentials ${username} --client-certificate="${username}.crt" --client-key="${username}.key" --embed-certs
kubectl --kubeconfig=${username}-kubeconfig config set-context cluster-a-${username} --user=${username} --cluster=cluster-a
kubectl --kubeconfig=${username}-kubeconfig config use-context cluster-a-${username}

#echo "Creating namespace..."
#kubectl --kubeconfig=${admin_kubeconfig} create ns ${namespace}
#echo "done"

#echo "Creating rolebinding of regular for ${username}..."
#kubectl --kubeconfig=${admin_kubeconfig} -n $namespace create rolebinding ${username} --clusterrole=regular --user=${username}
#echo "done"

