#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for Dummy Serial Classes."""

import random
import unittest
import logging
import logging.handlers

from serial.serialutil import SerialException
import dummyserial

__author__ = 'Greg Albrecht <gba@orionlabs.io>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'

#Constants
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
NUMBERS = '0123456789'
POSITIVE_NUMBERS = NUMBERS[1:]
ALPHANUM = ''.join([ALPHABET, NUMBERS])


def dummy_method(x):
    return x

class DummySerialTest(unittest.TestCase):  # pylint: disable=R0904
    """Tests for Dummy Serial."""

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(dummyserial.constants.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(dummyserial.constants.LOG_LEVEL)
        _console_handler.setFormatter(dummyserial.constants.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    @classmethod
    def random(cls, length=8, alphabet=None):
        """
        Generates a random string for test cases.

        :param length: Length of string to generate.
        :param alphabet: Alphabet to use to create string.
        :type length: int
        :type alphabet: str
        """
        alphabet = alphabet or ALPHANUM
        return ''.join(random.choice(alphabet) for _ in range(length))
        

    def setUp(self):  # pylint: disable=C0103
        """
        Sets up test environment:

        1) Creates a random serial port name.
        2) Creates a random baud rate.
        """
        self.random_serial_port = self.random()
        self.random_baudrate = self.random(5,NUMBERS)
        self._logger.debug(
            'random_serial_port=%s random_baudrate=%s',
            self.random_serial_port,
            self.random_baudrate
        )

    def test_write_and_read(self):
        """Tests writing-to and reading-from a Dummy Serial port (just strings)"""
        rand_write_len1 = random.randint(0, 1024)
        rand_write_len2 = random.randint(0, 1024)
        rand_write_str1 = self.random(rand_write_len1).encode()
        rand_write_str2 = self.random(rand_write_len2).encode()

        ds_instance = dummyserial.Serial(
            port=self.random_serial_port,
            baudrate=self.random_baudrate,
            responses={rand_write_str1: rand_write_str2}
        )
       
        ds_instance.write(rand_write_str1)
        read_data = b''
        while 1:
            read_data = b''.join([read_data, ds_instance.read(rand_write_len2)])
            waiting_data = ds_instance.inWaiting()
            if not waiting_data:
                break

        self.assertEqual(read_data, rand_write_str2)
    

    def test_write_closed_port(self):
        """Tests writing-to a closed Dummy Serial port."""
        rand_write_len1 = random.randint(0, 1024)
        rand_write_len2 = random.randint(0, 1024)
        rand_write_str1 = self.random(rand_write_len1).encode()
        rand_write_str2 = self.random(rand_write_len2).encode()

        ds_instance = dummyserial.Serial(
            port=self.random_serial_port,
            baudrate=self.random_baudrate,
            responses={rand_write_str1: rand_write_str2}
        )

        self.assertTrue(ds_instance._isOpen)  # pylint: disable=W0212
        ds_instance.close()
        self.assertFalse(ds_instance._isOpen)  # pylint: disable=W0212
        with self.assertRaises(SerialException):
            ds_instance.write(rand_write_str1)
        self.assertFalse(ds_instance._isOpen)  # pylint: disable=W0212

    def test_write_and_read_to_closed_port(self):
        """Tests writing-to and reading-from a closed Dummy Serial port."""
        rand_write_len1 = random.randint(0, 1024)
        rand_write_len2 = random.randint(0, 1024)
        rand_write_str1 = self.random(rand_write_len1).encode()
        rand_write_str2 = self.random(rand_write_len2).encode()

        ds_instance = dummyserial.Serial(
            port=self.random_serial_port,
            baudrate=self.random_baudrate,
            responses={rand_write_str1: rand_write_str2}
        )

        self.assertTrue(ds_instance._isOpen)  # pylint: disable=W0212
        ds_instance.write(rand_write_str1)
        ds_instance.close()
        self.assertFalse(ds_instance._isOpen)  # pylint: disable=W0212
        with self.assertRaises(SerialException):
            ds_instance.read(rand_write_len2)
        self.assertFalse(ds_instance._isOpen)  # pylint: disable=W0212

    def test_repr_port(self):
        """Tests describing a Dummy Serial port."""
        rand_write_len1 = random.randint(0, 1024)
        rand_write_len2 = random.randint(0, 1024)
        rand_write_str1 = self.random(rand_write_len1).encode()
        rand_write_str2 = self.random(rand_write_len2).encode()

        ds_instance = dummyserial.Serial(
            port=self.random_serial_port,
            baudrate=self.random_baudrate,
            responses={rand_write_str1: rand_write_str2}
        )

        self.assertTrue(self.random_serial_port in str(ds_instance))

    def test_open_port(self):
        """Tests opening an already-open Dummy Serial port."""
        rand_write_len1 = random.randint(0, 1024)
        rand_write_len2 = random.randint(0, 1024)
        rand_write_str1 = self.random(rand_write_len1).encode()
        rand_write_str2 = self.random(rand_write_len2).encode()

        ds_instance = dummyserial.Serial(
            port=self.random_serial_port,
            baudrate=self.random_baudrate,
            responses={rand_write_str1: rand_write_str2}
        )

        self.assertTrue(ds_instance._isOpen)  # pylint: disable=W0212
        with self.assertRaises(SerialException):
            ds_instance.open()
        ds_instance.close()
        self.assertFalse(ds_instance._isOpen)  # pylint: disable=W0212
        ds_instance.open()
        self.assertTrue(ds_instance._isOpen)  # pylint: disable=W0212

    def test_close(self):
        """Tests closing a Dummy Serial port."""
        rand_write_len1 = random.randint(0, 1024)
        rand_write_len2 = random.randint(0, 1024)
        rand_write_str1 = self.random(rand_write_len1).encode()
        rand_write_str2 = self.random(rand_write_len2).encode()

        ds_instance = dummyserial.Serial(
            port=self.random_serial_port,
            baudrate=self.random_baudrate,
            responses={rand_write_str1: rand_write_str2}
        )

        self.assertTrue(ds_instance._isOpen)  # pylint: disable=W0212
        self.assertFalse(ds_instance.close())
        self.assertFalse(ds_instance._isOpen)  # pylint: disable=W0212

    def test_write_and_read_no_data_present(self):  # pylint: disable=C0103
        """Tests writing and reading with an unspecified response."""
        rand_write_len1 = random.randint(256, 1024)
        rand_read_len2 = random.randint(1, 16) # give it some order of magnitudes less
        rand_write_str1 = self.random(rand_write_len1)

        ds_instance = dummyserial.Serial(
            port=self.random_serial_port,
            baudrate=self.random_baudrate
        )

        ds_instance.write(rand_write_str1)
        
        
        while 1:
            ds_instance.read(rand_read_len2) # discard this data
            if not ds_instance.inWaiting():
                empty_data = ds_instance.read(rand_read_len2)
                break

        self.assertEqual(
            dummyserial.constants.NO_DATA_PRESENT, empty_data)


if __name__ == '__main__':
    unittest.main()
