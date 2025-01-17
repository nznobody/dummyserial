#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Dummy Serial Class Definitions"""

import logging
import logging.handlers
import sys
import time

from serial.serialutil import SerialException, PortNotOpenError

import dummyserial.constants

__author__ = 'Greg Albrecht <gba@orionlabs.io>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'


class Serial(object):
    """
    Dummy (mock) serial port for testing purposes.

    Mimics the behavior of a serial port as defined by the
    `pySerial <http://pyserial.sourceforge.net/>`_ module.

    Attributes:
        ** port(str): Serial port
        ** timeout(int): Timeout in seconds (Default 2 seconds)
        ** responses(dict): Dictionary of response strings or method
        ** baudrate(integer): Baudrate (Default is 9600)

    Note:
    As the portname argument not is used properly, only one port on
    :mod:`dummyserial` can be used simultaneously.
    """

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(dummyserial.constants.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(dummyserial.constants.LOG_LEVEL)
        _console_handler.setFormatter(dummyserial.constants.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, *args, **kwargs):
        self._logger.debug('args=%s', args)
        self._logger.debug('kwargs=%s', kwargs)

        self._isOpen = True  # pylint: disable=C0103
        self._waiting_data = dummyserial.constants.NO_DATA_PRESENT

        self.port = kwargs['port']  # Serial port name.
        self.initial_port_name = self.port  # Initial name given to the port

        self.responses = kwargs.get('responses', {})
        self.timeout = kwargs.get(
            'timeout', dummyserial.constants.DEFAULT_TIMEOUT)
        self.baudrate = kwargs.get(
            'baudrate', dummyserial.constants.DEFAULT_BAUDRATE)

    def __repr__(self):
        """String representation of the DummySerial object."""
        return (
            "{0}.{1}<id=0x{2:x}, open={3}>(port={4!r}, timeout={5!r}, "
            "waiting_data={6!r})".format(
                self.__module__,
                self.__class__.__name__,
                id(self),
                self._isOpen,
                self.port,
                self.timeout,
                self._waiting_data,
            )
        )

    def open(self):
        """Open a (previously initialized) port."""
        self._logger.debug('Opening port')

        if self._isOpen:
            raise SerialException('Port is already open.')

        self._isOpen = True
        self.port = self.initial_port_name

    def close(self):
        """Close a port on dummy_serial."""
        self._logger.debug('Closing port')
        if self._isOpen:
            self._isOpen = False
        self.port = None

    def write(self, data):
        """
        Write to a port on dummy_serial.

        Args:
            data (string/bytes): data for sending to the port on
            dummy_serial. Will affect the response for subsequent read
            operations.

        Note that for Python2, the inputdata should be a **string**. For
        Python3 it should be of type **bytes** or **bytearray**.
        """
        
        if isinstance(data, bytearray):
            data = bytes(data)

        self._logger.debug('type(data): %s', type(data))
        if sys.version_info[0] > 2 and not isinstance(data, bytes):
            self._logger.debug('Writing str(%s): "%s"', len(data), data)
        else:
            self._logger.debug('Writing bytes(%s): %s', len(data), self._ashex(data))

        if not self._isOpen:
            raise PortNotOpenError

        self._waiting_data = self._check_response(data)
        return

    def read(self, size=1):
        """
        Read size bytes from the Dummy Serial Responses.

        The response is dependent on what was written last to the port on
        dummyserial, and what is defined in the :data:`RESPONSES` dictionary.

        Args:
            size (int): For compability with the real function.

        Returns a **string** for Python2 and **bytes** for Python3.

        If the response is shorter than size, it will sleep for timeout.

        If the response is longer than size, it will return only size bytes.
        """
        self._logger.debug('Reading %s bytes.', size)

        if not self._isOpen:
            raise PortNotOpenError

        if size < 0:
            raise dummyserial.exceptions.DSIOError(
                'The size to read must not be negative. ' +
                'Given: {!r}'.format(size))

        # Do the actual reading from the waiting data, and simulate the
        # influence of size.
        if self._waiting_data == dummyserial.constants.DEFAULT_RESPONSE:
            data_out = self._waiting_data
        elif size < len(self._waiting_data):
            self._logger.debug(
                'The size (%s) to read is smaller than the available data. ' +
                'Some bytes will be kept for later. ' +
                'Available (%s): "%s"',
                size, len(self._waiting_data), self._waiting_data
            )

            data_out = self._waiting_data[:size]
            self._waiting_data = self._waiting_data[size:]
        elif size == len(self._waiting_data):
            data_out = self._waiting_data
            self._waiting_data = dummyserial.constants.NO_DATA_PRESENT
        else:  # Wait for timeout - we asked for more data than available!
            self._logger.debug(
                'The size (%s) to read is larger than the available data. ' +
                'Will sleep until timeout. ' +
                'Available (%s): "%s"',
                size, len(self._waiting_data), self._waiting_data
            )

            time.sleep(self.timeout)
            data_out = self._waiting_data
            self._waiting_data = dummyserial.constants.NO_DATA_PRESENT

        self._logger.debug(
            'Read (%s): "%s"',
            len(data_out), data_out
        )

        # if sys.version_info[0] > 2 and not isinstance(data_out, bytes):  # Convert types to make it python3 compat.
        #     return bytes(data_out, encoding='latin1')
        # else:
        return data_out

    def inWaiting(self):  # pylint: disable=C0103
        """Returns length of waiting output data. pyserial 2.7 method"""
        return len(self._waiting_data)

    @property
    def in_waiting(self):    
        return self.inWaiting()

    def _check_response(self, data_in):

        data_out = dummyserial.constants.NO_DATA_PRESENT
        if data_in in self.responses:
            data_out = self.responses[data_in]

        return data_out

    def _ashex(self, msg):
        return " ".join(["{:02X}".format(x) for x in msg])

