#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/home/hc/hc/climax_svr

source /home/hc/Env/hc/bin/activate
nohup python -u rpt_svr.py &

