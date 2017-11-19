import inspect
import time
from Queue import Queue
from logging import getLogger
from threading import Thread

import serial


class ArduinoTimeoutRelaysInitError(Exception):
    pass


class ArduinoTimeoutRelaysCommandError(Exception):
    pass


INIT_STRING = 'DEBUG: setup() complete'


class ArduinoTimeoutRelays(Thread):
    def __init__(self, port):
        super(ArduinoTimeoutRelays, self).__init__()

        self._port = port

        self._serial = None
        self._stopped = None
        self._start_queue = Queue()

        self._logger = getLogger(self.__class__.__name__)
        self._logger.debug('{0}(); port={1}'.format(
            inspect.currentframe().f_code.co_name, self._port
        ))

    def open(self):
        self.start()
        self._start_queue.get()

    def close(self):
        self._stopped = True
        self.join()

    def relay_on(self, relay):
        self._serial.write('{0},on\n'.format(relay))
        data = self._serial.readline().strip()
        if not data.startswith('INFO: '):
            raise ArduinoTimeoutRelaysCommandError('relay_on failed; Arduino said: {0}'.format(repr(data.strip())))

        return True

    def relay_off(self, relay):
        self._serial.write('{0},off\n'.format(relay))
        data = self._serial.readline().strip()
        if not data.startswith('INFO: '):
            raise ArduinoTimeoutRelaysCommandError('relay_off failed; Arduino said: {0}'.format(repr(data.strip())))

        return True

    def _init(self):
        self._serial = serial.Serial()

        self._serial.port = self._port
        self._serial.baudrate = 9600
        self._serial.bytesize = serial.EIGHTBITS
        self._serial.parity = serial.PARITY_NONE
        self._serial.stopbits = serial.STOPBITS_ONE
        self._serial.timeout = 5
        self._serial.xonxoff = 0
        self._serial.rtscts = 0

        self._serial.open()

        self._serial.setDTR(False)
        time.sleep(1)

        self._serial.setDTR(True)
        time.sleep(1)

        try:
            data = self._serial.readline()
            if data.strip() != INIT_STRING:
                raise ArduinoTimeoutRelaysInitError(
                    'expected {0} during init, got {1}'.format(
                        repr(INIT_STRING), repr(data)
                    )
                )
        except Exception:
            raise ArduinoTimeoutRelaysInitError('timed out waiting for {0}'.format(
                repr(INIT_STRING)
            ))

        self._start_queue.put('started')

    def run(self, test_mode=False):
        self._stopped = False

        self._init()

        while not self._stopped:
            time.sleep(1)

            if test_mode:
                break


if __name__ == '__main__':
    import sys

    try:
        port = sys.argv[1]
    except:
        port = '/dev/ttyACM0'

    a = ArduinoTimeoutRelays(port)
    a.open()

    for i in range(1, 5):
        a.relay_on(i)
        time.sleep(1)

    a.close()
