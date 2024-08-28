#!/bin/bash

NAMESPACE=kube-system
pod="";
result="";

get_pod () {

    if kubectl get pods --namespace $NAMESPACE | grep -E -o -q "$1-[0-9].\S*"
    then
        pod=$(kubectl get pods --namespace $NAMESPACE | grep -E -o "$1-[0-9].\S*")
    else
        pod=$(kubectl get pods --namespace $NAMESPACE | grep -E -o "$1-[A-Za-z].\S*")
    fi
}

check_deleted_pod () {

    if [[ $1 == *"deleted"* ]];
    then
        echo -e $2 "deleted.\n"
    else
        echo -e $2 "failed to delete. Please investigate.\n"
        exit 1
    fi
}

delete_pod () {

    get_pod $1
    echo deleting $1 pod - $pod in namespace $NAMESPACE
    result=$(kubectl delete pod $pod --namespace $NAMESPACE)
    check_deleted_pod "$result" $1


}

delete_pod "csi-cinder-controllerplugin"