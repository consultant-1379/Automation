#!/usr/bin/env bash

# script used in jenkins jobs to
# copy cucumber report file
# cucumber.sh is part of automation code repo
# Each workspace will have its own cucumber.sh that will help in running cocurrent jobs

ENV_NAME=$1
JOB_NAME=$2

EIFFEL_FOLDER="/proj/eiffel052_config_fem1s11"
REPORTS_FOLDER="$EIFFEL_FOLDER/eiffel_home/userContent/automation_reports"
WS_REPORTS_FOLDER="cucumber_reports"
DIRECTORY="$REPORTS_FOLDER/$ENV_NAME"

echo
echo "Preparing Cucumber Reports"
echo "=========================="
echo "Environment: ${ENV_NAME}"
echo "Job: ${JOB_NAME}"
echo "=========================="

if [ "${ENV_NAME}" == '' ]; then
    echo "Empty env name"
    exit
fi

if [ ! -d "${DIRECTORY}" ]; then
   echo "creating directory ${DIRECTORY}"
   mkdir "${DIRECTORY}" && chmod 777 "${DIRECTORY}"
fi

echo "Copy"
echo "${WS_REPORTS_FOLDER}/cucumber.json"
echo "to"
echo "${REPORTS_FOLDER}/${ENV_NAME}/${JOB_NAME}.json"

cp "${WS_REPORTS_FOLDER}"/cucumber.json "${REPORTS_FOLDER}/${ENV_NAME}/${JOB_NAME}".json

echo
