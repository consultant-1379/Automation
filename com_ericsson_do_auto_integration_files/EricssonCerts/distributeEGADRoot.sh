#!/usr/bin/env bash
# ********************************************************************
# Ericsson LMI                                    SCRIPT
# ********************************************************************
#
# (c) Ericsson LMI 2021
#
# The copyright to the computer program(s) herein is the property of
# Ericsson LMI. The programs may be used and/or copied only  with the
# written permission from Ericsson LMI or in accordance with the terms
# and conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
#
# ********************************************************************
# created by eedmae, 2020-02-18 17:13
# script to distribute
#  a) the Root cert of self signed certs in the CCD cluster
#     this is required when using self signed certs like the internally signed Ericsson certs signed by EGAD
#  b) to place the EGAD Root cert into the docker ca

set -e
export LANG=en_US.UTF-8     # getting rid of warnings from perl
export LC_ALL=en_US.UTF-8

REGISTRY_HOST=${1:?"please provide registry URL. Example: registry.ccd1.gic.ericsson.se"}

# do not bother about log in messages (-q), the knownhosts file and host key checking
SSH_OPTS=" -q -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "
SSH="ssh ${SSH_OPTS}"
SCP="scp ${SSH_OPTS}"

ROOT_CERTS_DIR="/home/eccd/EricssonCerts"
TEST_CERT="${ROOT_CERTS_DIR}/test_bundle.cer"  # a cert that has been signed by EGAD
EGAD_ROOT="${ROOT_CERTS_DIR}/EGAD_bundle.cer"  # this is a bundle of the EGADIssuerCA3.cer and the EGADRoot.cer


# get internal IPs of all masters and workers
# Note: probably we don't have to run this on the masters
# Note: we probably should run this on both directors
NODE_IPS=$(kubectl get nodes  -o jsonpath='{.items[?(@.metadata.name>="worker-")].status.addresses[?(.type=="InternalIP")].address} ' )

DOCKER_REG_DIR="/etc/docker/certs.d/${REGISTRY_HOST}"

for NODE in ${NODE_IPS}
do
  echo "Host: >${NODE}<"
  echo will copy the certs to the host
  eval "${SCP} -r ${ROOT_CERTS_DIR} [${NODE}]:"
  echo will place the EGAD bundle in the OS ca
  eval "${SSH} ${NODE} sudo cp ${ROOT_CERTS_DIR}/*.cer /etc/pki/trust/anchors/; sudo update-ca-certificates; " || (echo "[FAIL]" ; exit 1)
  echo "Restarting containerd to refresh certs"
  eval "${SSH} ${NODE} sudo systemctl restart containerd;" || (echo "[If CCD below 2.18 version, containerd will not restart... Continuing...]" ;)
  echo will test if that was successful
  eval "${SSH} ${NODE} openssl verify ${TEST_CERT} " || (echo "[FAIL]" ; exit 1)
  echo "will now place the same EGAD root bundle in docker\'s cert.d"
  eval "${SSH} ${NODE} sudo mkdir -p ${DOCKER_REG_DIR}" || (echo "[FAIL]" ; exit 1)
  eval "${SSH} ${NODE} sudo cp ${EGAD_ROOT} ${DOCKER_REG_DIR}/ca.crt" || (echo "[FAIL]"; exit 1)

done
