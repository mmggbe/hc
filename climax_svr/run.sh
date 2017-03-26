#!/bin/bash

RUN= python3 webserver.py --host 192.168.157.4 --port 8080 --level debug

echo $RUN
$RUN

