#!/usr/bin/env python3
#
# serpent.py
#
# NOTE: THIS FILE IS INTENDED TO BE USED AS A STANDALONE COMMAND-LINE PROGRAM.
#
# If you want to implement serpent into your own tool, it is highly recommended
# that you call the functions separately rather than import this file. See
# README.md for more information.
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
import argparse

# Import serpent stuff
from tokenizer import tokenize, TokenError
from compiler import compile_hsc_script, CompileError
from error import show_message_for_character, error
from parser import parse_serpent_script, ParserError

# Entry point
def serpent():
    parser = argparse.ArgumentParser(description="Serpent version 2.0.0")
    parser.add_argument("input", help="Path to input script")
    parser.add_argument("output", help="Path to output script")
    args = parser.parse_args()

    # Get the tokens
    tokens = []
    lines = []

    # Open the thing
    try:
        with open(args.input, "r") as f:
            line = 0
            text = f.readline()
            while text != "":
                line = line + 1
                try:
                    tokens.extend(tokenize(text, line))
                except TokenError as e:
                    error("An error occurred when tokenizing: {:s}".format(e.message))
                    show_message_for_character(line, e.character, text, e.message_under)
                    return

                lines.append(text)
                text = f.readline()
    except FileNotFoundError as e:
        error("An error occurred while opening: {:s}".format(str(e)))
        return

    # Parse it
    parsed = None
    try:
        parsed = parse_serpent_script(tokens)
    except ParserError as e:
        error("An error occurred when parsing: {:s}".format(e.message))
        show_message_for_character(e.token.line, e.token.character, lines[e.token.line - 1], e.message_under)
        return

    # Make it into a hsc thing
    compiled = None
    try:
        compiled = compile_hsc_script(parsed)
    except CompileError as e:
        error("An error occurred when compiling: {:s}".format(e.message))
        return

    # Save
    with open(args.output,"w+") as f:
        f.write(compiled + "\n")

# Entry point
if __name__ == "__main__":
    serpent()
