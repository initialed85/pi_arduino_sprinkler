# pi_arduino_sprinkler (work in progress)

Some code to automate an existing sprinkler system using a Raspberry Pi to talk to OpenWeatherMap and an Arduino
to talk to the pumps.

If we take my use case as an example- I had an old and broken sprinkler controller but (as I discovered when everything
malfunctioned one day) the 24VAC transformer and the pumps all seem to still work.

I intend to use a 24VAC rectifier with two 5V regulators (thanks young kid at Altronics) to power both the Raspberry
Pi and the Arduino from the same 24VAC that will be switched through to the pumps via some relays.

Here in Perth, you're only allowed to water on certain days at certain hours, so it's important for this system to
adhere to those rules; here's how I propose to achieve that:

* The Pi will have a schedule manually set and it'll also sync with OpenWeatherMap to defer watering if it has rained
or is due to rain
* The Pi will send regular messages to the Arduino about the state the relays should be in (either on or off)
* If the Pi fails to send messages to the Arduino, the code on the Arduino will time the relays out after 30 seconds
* If the Arduino loses power, the relays will open (turning off the pumps)    

## Prequisites (hardware)

* 1 x [Raspberry Pi](https://www.raspberrypi.org/); I've used a Pi 3
* 1 x [Arduino](https://www.arduino.cc/); I've used part [Z6240 from Altronics](http://www.altronics.com.au/p/z6240-funduino-uno-r3-compatible-development-board/)
* 1 x 4 channel 5VDC relay board; I've used part [Z6237 from Altronics](http://www.altronics.com.au/p/z6327-4-channel-5v-relay-control-board/)
* 1 x 400V 4A bridge rectifier; I've used part [KBL404 from Altronics](http://www.altronics.com.au/p/z0076-kbl404-400v-4a-plastic-bridge-rectifier/)
* 2 x 5V 1A regulators; I've used part [Z0505 from Altronics](http://www.altronics.com.au/p/z0505-7805-5v-1-amp-to-220-fixed-voltage-regulator/)
* 6 x male-to-female jumper leads
* USB-A to USB-B cable (normally provided with an Arduino)

## Prerequisites (software)

* on your PC
    * Arduino IDE to flash the Arduino (only required once)
* on the Pi
    * supervisor
        * ```apt-get install supervisor```
    * pip 
        * ```apt-get install pip```
    * virtualenvwrapper
        * ```pip install virtualenvwrapper```
    
### How to setup for testing (hardware)

* with the Arduino powered off
    * connect the relay board to the Arduino in the following way (relay board left, Arduino right)
        * VCC -> Vin
        * GND -> GND
        * IN1 -> DIGITAL 2
        * IN2 -> DIGITAL 3
        * IN3 -> DIGITAL 4
        * IN4 -> DIGITAL 5
* with the Arduino powered on and connected to your PC via USB
    * in the Arduino IDE
        * open `arduino_timeout_relays/arduino_timeout_relays.ino` and upload it to the device
        * open the Serial Monitor and test all the relays by sending the following four lines
            * `1,on` 
            * `2,on` 
            * `3,on` 
            * `4,on`
        * each relay should come on the moment you hit enter
        * each relay should turn off 30 seconds after it was turned on (as a fail-safe against water wasteage in the
        event that the Pi fails)

At this point the Arduino should be proven, so unplug it from your computer and plug it into the Pi.

### How to setup for testing (software)

These steps will assume you're on a Raspberry Pi running Raspbian Lite as the "pi" user.

* pull this repo down
    * ```git clone https://github.com/initialed85/pi_arduino_sprinkler```
* change the pulled folder
    * ```cd pi_arduino_sprinkler```
* create a Virtualenv
    * ```mkvirtualenv pi_arduino_sprinkler```
* install the pip requirements
    * ```pip install -r requirements.txt```
* confirm the Pi can talk to the Arduino
    * ```python -m pi_sprinklers.arduino_timeout_relays```
        * after some setup time, all four relays should click on
        * the Python script should quit
        * after 30 seconds, all four relays should turn off
<!---
* install the supervisor config file
    * ```sudo cp pi_arduino_sprinkler.conf /etc/supervisor/conf.d/```
* copy example_config.py to config.py and make the necessary edits; of note:
    * OWM_KEY (sign up at [OpenWeatherMap](http://www.openweathermap.com/))
    * LAT and LON of the location you want to pull weather for
    * UUID of the target [http://zmote.io/](zmote.io) device
    * DAYS_OF_THE_WEEK watering is allowed
    * HOURS_TO_WAIT_AFTER_SUNSET before turning the sprinklers on
    * WATERING_DURATION in minutes watering is allowed
* reload the supervisor config file
    * ```sudo supervisorctl reread```
    * ```sudo supervisorctl update```
    
At this point, you should now be running- validate by looking at ```/tmp/supervisor_stderr_pi_arduino_sprinkler.log```
--->