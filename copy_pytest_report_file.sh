env_name=$1
job_name=$2
report_path=$3
target_slave=$4

echo $env_name
echo $job_name
echo $report_path
echo $target_slave

DIRECTORY="$report_path/$env_name"
echo $DIRECTORY
if [$env_name == ""]; then
    echo "Empty env name"
    exit
fi

if [ ! -d "$DIRECTORY" ]; then
   mkdir $DIRECTORY
   echo $DIRECTORY
   echo "directory created"
   chmod 777 $DIRECTORY
fi

rm -rf $report_path/$env_name/$job_name

cp -r /proj/eiffel052_config_fem1s11/slaves/$target_slave/workspace/$job_name/allure_reports $report_path/$env_name/$job_name

echo "Report file transffered succesfully"