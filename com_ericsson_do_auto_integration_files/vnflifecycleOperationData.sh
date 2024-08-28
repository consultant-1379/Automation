#!/bin/sh 



export PGPASSWORD='vnflaf123'



psql -h $POSTGRES_HOST -U vnflaf -w -p 5432 -d vnflafdb -c "select vnflifecycleoperationid,vnfid,workflowbundleversion,businesskey  from vnflifecycleoperation where  vnfid ='$1' and businesskey  LIKE '%$2%'" 
