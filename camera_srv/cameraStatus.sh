#!/bin/bash

source /home/hc/Env/cam/bin/activate
export PYTHONPATH=$PYTHONPATH:/home/hc/uat/hc/climax_web:/home/hc/uat/hc/climax_svr


python3 -u /home/hc/uat/hc/camera_srv/cameraStatus.py
