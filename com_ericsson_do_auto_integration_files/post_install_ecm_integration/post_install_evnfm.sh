#!/usr/bin/env bash

NAMESPACE=$1
NFVO_FQDN=$2
USER=$3

#### FETCH CERT FROM NFVO ####
# commented out below line for ticket SM-95464 , now onwards will use tls.cert provided by eo-staging
#openssl s_client -connect ${NFVO_FQDN}:443 </dev/null 2>/dev/null | openssl x509 -outform PEM > tls.crt

#### CREATE THE SECRET TO CONNECT TO NFVO

# CHECK IF SECRET EXIST, IF NOT CREATE
NFVO_SECRET_EXIST=`kubectl get secret eric-eo-evnfm-nfvo -n "${NAMESPACE}" 2>&1`
echo "$NFVO_SECRET_EXIST"
if [[ $NFVO_SECRET_EXIST == *"(NotFound): secrets"* ]]; then
  kubectl create secret generic eric-eo-evnfm-nfvo --from-literal=nfvo.username=ecmadmin --from-literal=nfvo.password=CloudAdmin123 --from-literal=nfvo.tenantId=ECM --from-file=./tls.crt --namespace "${NAMESPACE}"
fi



#### CREATE CONFIG MAP ####

# CHECK IF CONFIGMAP EXISTS, IF NOT CREATE
CONFIG_MAP_EXISTS=`kubectl get configmap eric-eo-evnfm-nfvo-config  -n "${NAMESPACE}" 2>&1`
echo "$CONFIG_MAP_EXISTS"
if [[ $CONFIG_MAP_EXISTS == *"(NotFound): configmaps"* ]]; then
  sed -e "s/<NFVO_FQDN>/${NFVO_FQDN}/g" /home/"${USER}"/post_install_ecm_integration/eric-eo-evnfm-nfvo-config.yaml | kubectl create -n "${NAMESPACE}" -f -
fi
