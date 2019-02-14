#!/usr/bin/env python3
#
# Serpent version 1.1.0
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

# Import serpent stuff
from compiler import compile_script
from error import show_message_for_character, error
from parser import parse, ParserError
from tokenizer import tokenize, TokenError

def serpent(args):
    # Make sure we have the right number of arguments
    if len(args) != 3:
        print("Serpent version 1.2.0 by Kavawuvi (2019-02-13)", file=sys.stderr)
        print(args[0] + " <input-script> <output-script>", file=sys.stderr)
        return

    # Get the tokens
    tokens = []
    lines = []
    with open(args[1], "r") as f:
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

    # Parse it
    parsed = None
    try:
        parsed = parse(tokens)
    except ParserError as e:
        error("An error occurred when parsing: {:s}".format(e.message))
        show_message_for_character(e.token.line, e.token.character, lines[e.token.line - 1], e.message_under)
        return

    # Make it into a hsc thing
    compiled = compile_script(parsed)
    with open(args[2],"w+") as f:
        f.write(compiled + "\n")

# Entry point
if __name__ == "__main__":
    serpent(sys.argv)
