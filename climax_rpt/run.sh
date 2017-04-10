#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/home/marc/workspace/climax_svr
RUN= python3 rpt_svr.py

echo $RUN
$RUN

