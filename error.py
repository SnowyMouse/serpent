#!/usr/bin/env python3
#
# error.py
#
# Copyright (c) 2019 Kavawuvi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys

# Show a warning
def warning(message):
    print("(v)> WARNING: {:s}".format(message), file=sys.stderr)

# Show an error
def error(message):
    print("(X)> ERROR: {:s}".format(message), file=sys.stderr)

# Show this message for a character
#
# show_message_for_character(1, 5, "hello world", "Hi!") results in:
# 1:5: hello world
#          ^ Hi!
def show_message_for_character(line, character, text, message):
    line_char = "{:d}:{:d}: ".format(line, character)
    print("{:s}{:s}".format(line_char, text[:-1]), file=sys.stderr)
    print(("{:>" + str(len(line_char) + character - 1) + "s}^ {:s}").format("", message), file=sys.stderr)
