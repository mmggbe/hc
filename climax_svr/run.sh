#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/home/marc/workspace/climax_web
RUN= python3 polling_svr.py --host 192.168.157.4 --port 8080 --level debug

echo $RUN
$RUN

