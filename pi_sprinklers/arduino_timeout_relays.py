import inspect
import logging
import time
from Queue import Queue
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

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug('{0}(); port={1}'.format(
            inspect.currentframe().f_code.co_name, self._port
        ))

    def open(self):
        self._logger.debug('{0}()'.format(
            inspect.currentframe().f_code.co_name
        ))

        self.start()
        self._start_queue.get()

    def close(self):
        self._logger.debug('{0}()'.format(
            inspect.currentframe().f_code.co_name
        ))

        self._stopped = True
        self.join()

    def _empty_buffer(self):
        self._logger.debug('{0}()'.format(
            inspect.currentframe().f_code.co_name
        ))

        data = ''
        while self._serial.in_waiting > 0:
            data += self._serial.read(1)

        self._logger.debug('{0}(); data={1}'.format(
            inspect.currentframe().f_code.co_name, repr(data)
        ))

    def relay_on(self, relay):
        self._logger.debug('{0}()'.format(
            inspect.currentframe().f_code.co_name
        ))

        self._empty_buffer()

        self._serial.write('{0},on\n'.format(relay))
        data = self._serial.readline().strip()

        self._logger.debug('{0}(); data={1}'.format(
            inspect.currentframe().f_code.co_name, repr(data)
        ))

        if not data.startswith('INFO: '):
            self._logger.critical('{0}(); Arduino did not respond with expected response'.format(
                inspect.currentframe().f_code.co_name,
            ))
            raise ArduinoTimeoutRelaysCommandError('relay_on failed; Arduino said: {0}'.format(repr(data.strip())))

        return True

    def relay_off(self, relay):
        self._logger.debug('{0}()'.format(
            inspect.currentframe().f_code.co_name
        ))

        self._empty_buffer()

        self._serial.write('{0},off\n'.format(relay))
        data = self._serial.readline().strip()

        if not data.startswith('INFO: '):
            self._logger.critical('{0}(); Arduino did not respond with expected response'.format(
                inspect.currentframe().f_code.co_name,
            ))
            raise ArduinoTimeoutRelaysCommandError('relay_off failed; Arduino said: {0}'.format(repr(data.strip())))

        return True

    def _init(self):
        self._logger.debug('{0}()'.format(
            inspect.currentframe().f_code.co_name
        ))

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
            self._logger.critical('{0}(); data={1}'.format(
                inspect.currentframe().f_code.co_name, repr(data)
            ))
            if data.strip() != INIT_STRING:
                self._logger.critical('{0}(); Arduino did not respond with expected response'.format(
                    inspect.currentframe().f_code.co_name,
                ))
                raise ArduinoTimeoutRelaysInitError(
                    'expected {0} during init, got {1}'.format(
                        repr(INIT_STRING), repr(data)
                    )
                )
        except Exception:
            self._logger.critical('{0}(); Arduino did not respond before timeout'.format(
                inspect.currentframe().f_code.co_name,
            ))
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

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger = logging.getLogger(ArduinoTimeoutRelays.__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

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
