#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The Plaso Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This file contains a helper library to read binary files."""

import binascii
import logging
import os


def ByteStreamCopyToUtf16Stream(byte_stream, byte_stream_size=None):
  """Reads an UTF-16 formatted stream from a byte stream.

  The UTF-16 formatted stream should be terminated by an end-of-string
  character (\x00\x00). Otherwise the function reads upto the byte stream size.

  Args:
    byte_stream: The byte stream that contains the UTF-16 formatted stream.
    byte_stream_size: The byte stream size or None if the entire byte stream
                      should be read.

  Returns:
    String containing the UTF-16 formatted stream.
  """
  byte_stream_index = 0
  if not byte_stream_size:
    byte_stream_size = len(byte_stream)

  while byte_stream_index + 1 < byte_stream_size:
    if (byte_stream[byte_stream_index] == '\x00' and
        byte_stream[byte_stream_index + 1] == '\x00'):
      break

    byte_stream_index += 2

  return byte_stream[0:byte_stream_index]


def ReadUtf16Stream(file_object, offset=None, byte_size=0):
  """Reads an UTF-16 formatted stream from a file-like object.

  Reads an UTF-16 formatted stream that's terminated by
  an end-of-string character (\x00\x00) or upto the byte size.

  Args:
    file_object: A file-like object to read the data from.
    offset: An offset into the file object data, if -1 or not set
            the current location into the file object data is used.
    byte_size: Maximum number of bytes to read or 0 if the function
               should keep reading upto the end of file.

  Returns:
    An Unicode string.
  """
  if offset is not None:
    file_object.seek(offset, os.SEEK_SET)

  char_buffer = []

  stream_index = 0
  char_raw = file_object.read(2)
  while char_raw:
    if byte_size and stream_index >= byte_size:
      break

    if '\x00\x00' in char_raw:
      break
    char_buffer.append(char_raw)
    stream_index += 2
    char_raw = file_object.read(2)

  return ReadUtf16(''.join(char_buffer))


def Ut16StreamCopyToString(byte_stream, byte_stream_size=None):
  """Copies an UTF-16 formatted byte stream to a string.

  The UTF-16 formatted byte stream should be terminated by an end-of-string
  character (\x00\x00). Otherwise the function reads upto the byte stream size.

  Args:
    byte_stream: The UTF-16 formatted byte stream.
    byte_stream_size: The byte stream size or None if the entire byte stream
                      should be used.

  Returns:
    An Unicode string.
  """
  utf16_stream = ByteStreamCopyToUtf16Stream(
      byte_stream, byte_stream_size=byte_stream_size)

  try:
    return utf16_stream.decode('utf-16-le')
  except (UnicodeDecodeError, UnicodeEncodeError) as exception:
    logging.error(u'Unable to decode string: {0:s} with error: {1:s}'.format(
        HexifyBuffer(utf16_stream), exception))

  return utf16_stream.decode('utf-16-le', errors='ignore')


def ArrayOfUt16StreamCopyToString(byte_stream, byte_stream_size=None):
  """Copies an array of UTF-16 formatted byte streams to an array of strings.

  The UTF-16 formatted byte stream should be terminated by an end-of-string
  character (\x00\x00). Otherwise the function reads upto the byte stream size.

  Args:
    byte_stream: The UTF-16 formatted byte stream.
    byte_stream_size: The byte stream size or None if the entire byte stream
                      should be used.

  Returns:
    An array of Unicode strings.
  """
  array_of_strings = []
  utf16_stream_start = 0
  byte_stream_index = 0
  if not byte_stream_size:
    byte_stream_size = len(byte_stream)

  while byte_stream_index + 1 < byte_stream_size:
    if (byte_stream[byte_stream_index] == '\x00' and
        byte_stream[byte_stream_index + 1] == '\x00'):

      if byte_stream_index - utf16_stream_start <= 2:
        break

      array_of_strings.append(
          byte_stream[utf16_stream_start:byte_stream_index].decode(
          'utf-16-le'))
      utf16_stream_start = byte_stream_index + 2

    byte_stream_index += 2

  return array_of_strings


def ArrayOfUt16StreamCopyToStringTable(byte_stream, byte_stream_size=None):
  """Copies an array of UTF-16 formatted byte streams to a string table.

  The string table is a dict of strings with the byte offset as their key.
  The UTF-16 formatted byte stream should be terminated by an end-of-string
  character (\x00\x00). Otherwise the function reads upto the byte stream size.

  Args:
    byte_stream: The UTF-16 formatted byte stream.
    byte_stream_size: The byte stream size or None if the entire byte stream
                      should be used.

  Returns:
    A dict of Unicode strings with the byte offset as their key.
  """
  string_table = {}
  utf16_stream_start = 0
  byte_stream_index = 0
  if not byte_stream_size:
    byte_stream_size = len(byte_stream)

  while byte_stream_index + 1 < byte_stream_size:
    if (byte_stream[byte_stream_index] == '\x00' and
        byte_stream[byte_stream_index + 1] == '\x00'):

      if byte_stream_index - utf16_stream_start <= 2:
        break

      string = byte_stream[utf16_stream_start:byte_stream_index].decode(
          'utf-16-le')
      string_table[utf16_stream_start] = string
      utf16_stream_start = byte_stream_index + 2

    byte_stream_index += 2

  return string_table


def ReadUtf16(string_buffer):
  """Returns a decoded UTF-16 string from a string buffer."""
  if type(string_buffer) in (list, tuple):
    use_buffer = u''.join(string_buffer)
  else:
    use_buffer = string_buffer

  if not type(use_buffer) in (str, unicode):
    return u''

  try:
    return use_buffer.decode('utf-16').replace('\x00', '')
  except SyntaxError as exception:
    logging.error(u'Unable to decode string: {0:s} with error: {1:s}.'.format(
        HexifyBuffer(string_buffer), exception))
  except (UnicodeDecodeError, UnicodeEncodeError) as exception:
    logging.error(u'Unable to decode string: {0:s} with error: {1:s}'.format(
        HexifyBuffer(string_buffer), exception))

  return use_buffer.decode('utf-16', errors='ignore').replace('\x00', '')


def HexifyBuffer(string_buffer):
  """Return a string with the hex representation of a string buffer."""
  chars = []
  for char in string_buffer:
    chars.append(binascii.hexlify(char))

  return u'\\x{0:s}'.format(u'\\x'.join(chars))
