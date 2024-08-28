# awk check PODs status other than Completed and Running or PODs that restarted
awk_cmd = '$3 != "Completed" && $3 != "Running" || $4 != "0"  {print $0}'


# k8s get pods command
k8s_get_pod = 'kubectl get pod -n'
