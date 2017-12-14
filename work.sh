#!/bin/bash

source /root/.virtualenvs/pi_arduino_sprinkler/bin/activate

cd /home/edward/pi_arduino_sprinkler

# expects arguments like -r 1,30 -d 1 -r 1,30 -d 1
python -m pi_sprinklers.arduino_timeout_relays $@
