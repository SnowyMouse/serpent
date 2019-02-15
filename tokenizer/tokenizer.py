#!/usr/bin/env python3
#
# tokenizer/tokenizer.py
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
from error import warning, error, show_message_for_character
from .types import TokenError, TokenType, Token
from .symbols import EQUALITY_OPERATORS, RELATIONAL_OPERATORS, LOGICAL_OPERATORS, ARITHMETIC_SYMBOLS

# Function for when things mess up
def invalid_token_message(c, character, message):
    if c == "\n":
        c = "\\n"
    elif c == "\r":
        c = "\\r"
    elif c == "\t":
        c = "\\t"
    raise TokenError(character, "Unexpected character {:s}".format(c), message)

# Tokenize function
def tokenize(text, line):
    tokens = []
    token = Token()
    character = 0

    # Make the token
    for c in text:
        character = character + 1

        # Set character value for token
        if token.token == "":
            token.character = character

        # Strings
        if c == "\"":
            if token.token_type == TokenType.STRING:
                token.token += c
                tokens.append(token)
                token = Token()
            elif token.token_type == TokenType.OTHER or token.token_type == TokenType.INTEGER or token.token_type == TokenType.FLOAT:
                if token.token != "":
                    tokens.append(token)
                    token = Token()
                    token.character = character
                token.token_type = TokenType.STRING
                token.token += c
            elif token.token_type == TokenType.FLOAT_DECIMAL:
                invalid_token_message(c, character, "Expected number here")
            else:
                invalid_token_message(c, character, "Unexpected symbol here")
            continue

        # Whitespace
        if c.isspace():
            if token.token_type == TokenType.STRING:
                if c == "\n" or c == "\r":
                    invalid_token_message(c, character, "Unterminated string here")
                token.token += c
            elif token.token_type == TokenType.FLOAT_DECIMAL:
                invalid_token_message(c, character, "Expected number here")
            elif token.token != "":
                tokens.append(token)
                token = Token()
            continue

        # Anything here beyond here, if a string, should be in that string
        if token.token_type == TokenType.STRING:
            token.token += c
            continue

        # Numbers
        if c.isnumeric():
            if token.token_type == TokenType.INTEGER or token.token_type == TokenType.FLOAT:
                token.token += c
                continue
            elif (token.token_type == TokenType.OTHER and token.token == "") or token.token_type == TokenType.SYMBOL_OR_NUMBER:
                token.token_type = TokenType.INTEGER
                token.token += c
                continue
            elif token.token_type == TokenType.FLOAT_DECIMAL:
                token.token += c
                token.token_type = TokenType.FLOAT
                continue
            elif token.token_type == TokenType.OTHER:
                token.token += c
                continue
            elif token.token_type == TokenType.SYMBOL:
                tokens.append(token)
                token = Token()
                token.character = character
                token.token = c
                token.token_type = TokenType.INTEGER
                continue

        # Letters and underscores
        if c.isalpha() or c == "_":
            if token.token_type == TokenType.INTEGER or token.token_type == TokenType.FLOAT or token.token_type == TokenType.FLOAT_DECIMAL:
                invalid_token_message(c, character, "Expected number here")
            elif token.token_type == TokenType.SYMBOL:
                tokens.append(token)
                token = Token()
                token.character = character
                token.token = c
                token.token_type = TokenType.OTHER
            elif token.token_type == TokenType.OTHER:
                token.token += c
            else:
                invalid_token_message(c, character, "This is bad")
            continue

        # Symbols that can be combined
        if c == "=" or c == ">" or c == "<" or c == "&" or c == "|" or c in ARITHMETIC_SYMBOLS or c == "!":
            if token.token_type == TokenType.SYMBOL:
                token.token += c
            elif token.token_type == TokenType.INTEGER or token.token_type == TokenType.FLOAT or token.token_type == TokenType.OTHER:
                if token.token != "":
                    tokens.append(token)
                    token = Token()
                    token.character = character
                token.token = c
                # Could be a negative number
                if c == "-":
                    token.token_type = TokenType.SYMBOL_OR_NUMBER
                else:
                    token.token_type = TokenType.SYMBOL
            elif token.token_type == TokenType.FLOAT_DECIMAL:
                invalid_token_message(c, character, "Expected number here")
            else:
                invalid_token_message(c, character, "Unexpected symbol here")
            continue

        # Symbols that cannot be combined
        if c == "(" or c == ")" or c == ",":
            if token.token_type == TokenType.FLOAT_DECIMAL:
                invalid_token_message(c, character, "Expected number here")
            else:
                if token.token != "":
                    tokens.append(token)
                    token = Token()
                    token.character = character
                token.token = c
                token.token_type = TokenType.SYMBOL
                tokens.append(token)
                token = Token()
                continue

        # Decimals
        if c == ".":
            if token.token_type == TokenType.INTEGER:
                token.token_type = TokenType.FLOAT_DECIMAL
                token.token += c
                continue
            else:
                invalid_token_message(c, character, "Unexpected symbol here")

        # Comments
        if c == "#":
            if token.token_type == TokenType.FLOAT_DECIMAL:
                invalid_token_message(c, character, "Expected number here")
            elif token.token != "":
                tokens.append(token)
            break

        invalid_token_message(c, character, "Unknown token here")

    # Set line for tokens. Also, if SYMBOL_OR_NUMBER, then it's a SYMBOL
    for token in tokens:
        token.line = line
        if token.token_type == TokenType.SYMBOL_OR_NUMBER:
            token.token_type = TokenType.SYMBOL

    return tokens
