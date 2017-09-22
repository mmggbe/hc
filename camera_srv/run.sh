#!/bin/bash

function help {
    echo -e "\nrun: invalid argument\n"
    echo -e "\tUsage: run.sh start | stop | status \n"
}

function stopProcess {
    echo "Stop the process"
    kill -9 $(<run.pid)
    rm run.pid
}

function processStatus {
    if [ -e run.pid ]
    then
        if netstat -antp 2>&1 | grep 0.0.0.0:8000 | grep $(<run.pid)/python > /dev/null
        then
            echo "status: up"
        else
            echo "error: pid file but port not open"
        fi
    else
        if netstat -antp 2>&1 | grep 0.0.0.0:8000
        then
            echo "error no pid file but port open"
        else
            echo "status: down"
        fi
    fi
}

if [ $# -eq 1 ]
then
    if [ $1 = "start" ]
    then
        echo "Start ..."
        if [ -e run.pid ]
        then
            echo "Process already running"
            stopProcess
            echo "restart the process"
        fi
        source /home/hc/Env/hc/bin/activate
        nohup python -u cameraServer.py > /dev/null 2>&1 & echo $! > run.pid
    elif [ $1 = "stop" ]
    then
        if [ -e run.pid ]
        then
            stopProcess
        else
            echo "Process not running"
        fi
    elif [ $1 = "status" ]
    then
        processStatus
    else
        help
    fi
    
else
    help
fi
