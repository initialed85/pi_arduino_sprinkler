#!/bin/bash

source /root/.virtualenvs/pi_arduino_sprinkler/bin/activate

cd /home/edward/pi_arduino_sprinkler

# expects arguments like -r 1,3 -d 30 -r 1,2 -d 30
python -m pi_sprinklers.arduino_timeout_relays $@
