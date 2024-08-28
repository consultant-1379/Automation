#!/bin/bash

set -e

if [[ -z ${1+x} ]]; then
    echo "Namespace must be specified."
    exit 1
fi


NAMESPACE=$1

date '+%F %T'

echo "Deleting all resources in namespace ${NAMESPACE}"
echo "Listing all resources in namespace ${NAMESPACE}"
for i in $(kubectl api-resources --verbs=list --namespaced -o name | grep -v "events.events.k8s.io" | grep -v "events" | sort | uniq); do
    echo "Resource:" $i
    kubectl -n ${NAMESPACE} delete --all ${i}
done
echo
echo
echo "Deployment and resources have been deleted, proceeding with verification."
date '+%F %T'
