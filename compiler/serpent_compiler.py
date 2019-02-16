#!/usr/bin/env python3
#
# parser/serpent_compiler.py
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

from tokenizer import Token, TokenType, ARITHMETIC_SYMBOLS
from parser import Statement, StatementType
from .types import CompileError

# Translate a statement tree or token into its serpent equivalent
def compile_script(statement, level = 0):
    if isinstance(statement, Token):
        return str(statement.token)
    else:
        compiled = ""
        type = statement.statement_type

        # Main script
        if type == StatementType.MAIN_SCRIPT_BLOCK:
            for c in statement.children:
                compiled = compiled + compile_script(c, level) + "\n"

            return compiled

        # Global definition
        elif type == StatementType.GLOBAL_DEFINITION:
            return "global {:s} {:s} = {:s}".format(statement.global_type, statement.global_name, compile_script(statement.children[0]))

        # Expression
        elif type == StatementType.EXPRESSION:
            return compile_script(statement.children[0])

        # Script definition
        elif type == StatementType.SCRIPT_DEFINITION:
            compiled = statement.script_type + " ";
            if statement.script_type == "stub" or statement.script_type == "static":
                compiled = compiled + statement.script_return_type + " "
            compiled = compiled + statement.script_name + compile_script(statement.children[0], level)
            return compiled

        # Script block
        elif type == StatementType.SCRIPT_BLOCK:
            for c in statement.children:
                compiled = compiled + "\n" + generate_spaces(level + 1) + compile_script(c, level + 1)
            return compiled + generate_spaces(level) + "end"

        # Function call
        elif type == StatementType.FUNCTION_CALL:
            if statement.function_name == "set":
                return "{:s} = {:s}".format(compile_script(statement.children[0], level), compile_script(statement.children[1], level))
            elif statement.function_name == "not":
                return "!{:s}".format(compile_script(statement.children[0], level))
            elif statement.function_name == "=" or statement.function_name in ARITHMETIC_SYMBOLS:
                function_name = statement.function_name
                if function_name == "=":
                    function_name = "=="
                return "({:s} {:s} {:s})".format(compile_script(statement.children[0], level), function_name, compile_script(statement.children[1], level))

            compiled = statement.function_name + "("
            for c in range(len(statement.children)):
                compiled = compiled + compile_script(statement.children[c], level)
                if c + 1 < len(statement.children):
                    compiled = compiled + ", "
            return compiled + ")"

        # If statement
        elif type == StatementType.IF_STATEMENT:
            compiled = "if " + compile_script(statement.children[0], level)

            return "\n"


        else:
            raise CompileError("{:s} is unimplemented".format(type))

def generate_spaces(level):
    spaces = ""
    for i in range(level):
        spaces = spaces + "    "
    return spaces
