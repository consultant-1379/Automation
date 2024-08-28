#!/usr/bin/env bash

# script used in jenkins jobs to
# copy cucumber report file
# script location on jenkins slave:
# /proj/eiffel052_config_fem1s11/eiffel_home/userContent/cucumber.sh

env_name=$1
job_name=$2

echo "$env_name"
echo "$job_name"


DIRECTORY="/proj/eiffel052_config_fem1s11/eiffel_home/userContent/automation_reports/$env_name"
echo "$DIRECTORY"
if [ "$env_name" == '' ]; then
    echo "Empty env name"
    exit
fi

if [ ! -d "$DIRECTORY" ]; then
   mkdir "$DIRECTORY"
   echo "$DIRECTORY"
   echo "in the loop"
   chmod 777 "$DIRECTORY"
fi

cp /proj/eiffel052_config_fem1s11/slaves/EO-STAGING-SLAVE-2/workspace/"$job_name"/cucumber_reports/cucumber.json /proj/eiffel052_config_fem1s11/eiffel_home/userContent/automation_reports/"$env_name"/"$job_name".json
