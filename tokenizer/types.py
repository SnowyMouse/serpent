#!/usr/bin/env python3
#
# tokenizer/types.py
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

from enum import Enum

# Errors that may occur
class TokenError(Exception):
    message = "An error occurred"
    message_under = "This is where it occurred"
    character = 1
    def __init__(self, character, message, message_under):
        self.character = character
        self.message = message
        self.message_under = message_under
    def __str__(self):
        return "TokenError: {:s}".format(self.message)

# Types of tokens
class TokenType(Enum):
    OTHER = 0
    STRING = OTHER + 1
    INTEGER = STRING + 1
    FLOAT_DECIMAL = INTEGER + 1
    FLOAT = FLOAT_DECIMAL + 1
    SYMBOL = FLOAT + 1
    SYMBOL_OR_NUMBER = SYMBOL + 1

# Token class
class Token:
    token = ""
    token_type = TokenType.OTHER
    line = None
    character = 1
    def __repr__(self):
        return "<token=`" + self.token + "` type=" + str(self.token_type) + " at=" + str(self.line) + ":" + str(self.character) + ">"
