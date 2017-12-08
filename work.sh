#!/bin/bash

source /root/.virtualenvs/pi_arduino_sprinkler/bin/activate

cd /home/edward/pi_arduino_sprinkler

python -m pi_sprinklers.arduino_timeout_relays -r 1,2 -d 1 -r 1,3 -d 1
