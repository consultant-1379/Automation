if [ "$#" -ne 2 ]; then
    echo "Illegal number of arguments."
    echo "Namespace and Username must be specified."
    exit 1
fi

NAMESPACE=$1
USERNAME=$2
##### CREATE NAMESPACE #####
kubectl create namespace "${NAMESPACE}"

##### CREATE SECRETS FOR CCRC TRAFFIC #####
kubectl create secret generic eric-ccrc-nrf-sbi-server-certs-cacert --from-file=cacert=/home/"${USERNAME}"/CCRC_Pre_Reqs/ccrc_certs/ca-chain-cert.pem -n "${NAMESPACE}"
kubectl create secret tls eric-ccrc-nrf-sbi-server-certs --cert /home/"${USERNAME}"/CCRC_Pre_Reqs/ccrc_certs/server-cert.pem --key /home/"${USERNAME}"/CCRC_Pre_Reqs/ccrc_certs/server-key.pem -n "${NAMESPACE}"
kubectl create secret generic eric-ccrc-nrf-sbi-client-certs-cacert --from-file=ca-chain.cert.pem=/home/"${USERNAME}"/CCRC_Pre_Reqs/ccrc_certs/ca-chain-cert.pem -n "${NAMESPACE}"
kubectl create secret tls eric-ccrc-nrf-sbi-client-certs --cert /home/"${USERNAME}"/CCRC_Pre_Reqs/ccrc_certs/client-cert.pem --key /home/"${USERNAME}"/CCRC_Pre_Reqs/ccrc_certs/client-key.pem -n "${NAMESPACE}"
kubectl create secret generic eric-ccrc-nssf-sbi-server-certs-cacert --from-file=cacert=/home/"${USERNAME}"/CCRC_Pre_Reqs/ccrc_certs/ca-chain-cert.pem -n "${NAMESPACE}"
kubectl create secret tls eric-ccrc-nssf-sbi-server-certs --cert /home/"${USERNAME}"/CCRC_Pre_Reqs/ccrc_certs/server-cert.pem --key /home/"${USERNAME}"/CCRC_Pre_Reqs/ccrc_certs/server-key.pem -n "${NAMESPACE}"
kubectl create secret generic eric-ccrc-nssf-sbi-client-certs-cacert --from-file=ca-chain.cert.pem=/home/"${USERNAME}"/CCRC_Pre_Reqs/ccrc_certs/ca-chain-cert.pem -n "${NAMESPACE}"
kubectl create secret tls eric-ccrc-nssf-sbi-client-certs --cert /home/"${USERNAME}"/CCRC_Pre_Reqs/ccrc_certs/client-cert.pem --key /home/"${USERNAME}"/CCRC_Pre_Reqs/ccrc_certs/client-key.pem -n "${NAMESPACE}"


##### CREATE SECRET FOR DOCUMENT PG DB #####
kubectl create secret generic eric-data-document-database-pg-creds \
--from-literal=custom-user=customname --from-literal=custom-pwd=custompwd \
--from-literal=super-pwd=superpwd --from-literal=metrics-pwd=metricspwd \
--from-literal=replica-user=replicauser --from-literal=replica-pwd=replicapwd \
--namespace="${NAMESPACE}"


##### CREATE SECRET WITH ICCR CERT #####
kubectl create secret tls iccr-external-tls-secret --key /home/"${USERNAME}"/CCRC_Pre_Reqs/ccrc_certs/external.key --cert /home/"${USERNAME}"/CCRC_Pre_Reqs/ccrc_certs/external.crt -n "${NAMESPACE}"


##### CREATE SECRET FOR SNMP ALARM PROVIDER #####
kubectl create secret generic snmp-alarm-provider-config --namespace "${NAMESPACE}" --from-file=/home/"${USERNAME}"/CCRC_Pre_Reqs/config.json


##### CREATE SECRET FOR LDAP O&M PRE-DEPLOYMENT USER #####
kubectl create secret generic eric-data-distributed-coordinator-creds --namespace "${NAMESPACE}" --from-literal=etcdpasswd="$(echo -n "admin" | base64)"

kubectl create secret generic eric-sec-ldap-server-creds -n "${NAMESPACE}" --from-literal=adminuser=sysadmin \
--from-literal=adminpasswd=$6$Afe145T7$E64K9eLM7vO5W2rEA.8iuKf1bDKCqgU4/w60NKdsGsTfXuyuUpjt0odmY6rmQL.gpLGLKgt.ZdLjUglGp4mKi0 \
--from-literal=passwd=keycloak --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic eric-sec-access-mgmt-creds -n "${NAMESPACE}" --from-literal=kcadminid=admin --from-literal=kcpasswd=admin --dry-run=client -o yaml | kubectl apply -f -

##### Secret for Object Storage. The Object Storage MN service provides persistent object storage with data encryption
kubectl create secret generic eric-data-object-storage-mn-creds -n "${NAMESPACE}" --from-literal=accesskey=StorageAdmin --from-literal=secretkey=Pa$$w0rd4NEF

echo "All CCRC secrets created."
