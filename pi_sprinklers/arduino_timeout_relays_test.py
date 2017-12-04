import unittest

from hamcrest import equal_to, assert_that
from mock import patch, MagicMock, call

from pi_sprinklers.arduino_timeout_relays import ArduinoTimeoutRelays, StatefulArduinoTimeoutRelays


class ArduinoTimeoutRelaysTest(unittest.TestCase):
    def setUp(self):
        self._subject = ArduinoTimeoutRelays(
            port='/dev/ttyUSB999'
        )

        self._subject._serial = MagicMock()

    @patch('pi_sprinklers.arduino_timeout_relays.serial.Serial')
    def test_open(self, serial):
        self._subject._start_queue = MagicMock()
        self._subject.start = MagicMock()

        self._subject.open()

        assert_that(
            self._subject._start_queue.mock_calls,
            equal_to([
                call.get()
            ])
        )

        assert_that(
            self._subject.start.mock_calls,
            equal_to([
                call()
            ])
        )

    def test_close(self):
        self._subject_stopped = True
        self._subject.join = MagicMock()

        self._subject.close()

        assert_that(
            self._subject._stopped,
            equal_to(True)
        )

    def test_empty_buffer(self):
        self._subject._serial.in_waiting = 0
        self._subject._empty_buffer()

    def test_relay_on(self):
        self._subject._empty_buffer = MagicMock()
        self._subject._serial.readline.return_value = 'INFO: requesting relay 1 change to state on'

        assert_that(
            self._subject.relay_on(1),
            equal_to(True)
        )

    def test_relay_off(self):
        self._subject._empty_buffer = MagicMock()
        self._subject._serial.readline.return_value = 'INFO: requesting relay 1 change to state off'

        assert_that(
            self._subject.relay_off(1),
            equal_to(True)
        )

    @patch('pi_sprinklers.arduino_timeout_relays.time.sleep')
    def test_run(self, sleep):
        self._subject._init = MagicMock()

        self._subject.run(test_mode=True)

        assert_that(
            self._subject._init.mock_calls,
            equal_to([
                call()
            ])
        )

        assert_that(
            sleep.mock_calls,
            equal_to([
                call(1)
            ])
        )


class StatefulArduinoTimeoutRelaysTest(unittest.TestCase):

    @patch('pi_sprinklers.arduino_timeout_relays.ArduinoTimeoutRelays')
    def setUp(self, arduino_timeout_relays):
        self._subject = StatefulArduinoTimeoutRelays(
            port='/dev/ttyUSB999',
            num_relays=2,
        )

        assert_that(
            arduino_timeout_relays.mock_calls,
            equal_to([
                call(port='/dev/ttyUSB999')
            ])
        )

    def test_relay_on(self):
        self._subject.relay_on(1)

        assert_that(
            self._subject._relays_on,
            equal_to({1: True, 2: False})
        )

    def test_relay_off(self):
        self._subject.relay_off(1)

        assert_that(
            self._subject._relays_on,
            equal_to({1: False, 2: False})
        )

    def test_run_no_relays_on(self):
        self._subject.run(test_mode=True)

        assert_that(
            self._subject._arduino_timeout_relays.mock_calls,
            equal_to([
                call.open(),
                call.relay_off(1),
                call.relay_off(2),
                call.close()
            ])
        )

    def test_run_one_relay_on(self):
        self._subject.relay_on(1)

        self._subject.run(test_mode=True)

        assert_that(
            self._subject._arduino_timeout_relays.mock_calls,
            equal_to([
                call.open(),
                call.relay_on(1),
                call.relay_off(2),
                call.close()
            ])
        )

    def test_run_two_relays_on(self):
        self._subject.relay_on(1)
        self._subject.relay_on(2)

        self._subject.run(test_mode=True)

        assert_that(
            self._subject._arduino_timeout_relays.mock_calls,
            equal_to([
                call.open(),
                call.relay_on(1),
                call.relay_on(2),
                call.close()
            ])
        )
