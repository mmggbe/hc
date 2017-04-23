#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/home/hc/hc/climax_svr/GW_Crypto

source /home/hc/Env/hc/bin/activate
nohup python webserver.py --host horus.ovh --port 8080 --level debug &

