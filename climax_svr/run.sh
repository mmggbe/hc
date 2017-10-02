#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/home/hc/uat/hc/climax_svr/GW_Crypto:/home/hc/uat/hc/climax_web
source /home/hc/Env/uat/bin/activate

RUN= python3 -u polling_svr.py --host horus.ovh --port 8088 --level info &

echo $RUN
$RUN

