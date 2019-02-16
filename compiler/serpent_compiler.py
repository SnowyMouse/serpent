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
def compile_script(statement, beautify = False, level = 0):
    newline = "\n" if beautify else " "

    generate_spaces = do_generate_spaces if beautify else dont_generate_spaces

    if isinstance(statement, Token):
        return statement.token
    else:
        compiled = ""
        type = statement.statement_type

        # Main script
        if type == StatementType.MAIN_SCRIPT_BLOCK:
            for c in statement.children:
                compiled = compiled + compile_script(c, beautify, level) + newline

            return compiled

        # Global definition
        elif type == StatementType.GLOBAL_DEFINITION:
            format_string = "global {:s} {:s} = {:s}" if beautify else "global {:s} {:s}={:s}"
            return format_string.format(statement.global_type, statement.global_name, compile_script(statement.children[0], beautify, level))

        # Expression
        elif type == StatementType.EXPRESSION:
            return compile_script(statement.children[0], beautify, level)

        # Script definition
        elif type == StatementType.SCRIPT_DEFINITION:
            compiled = statement.script_type + " ";
            if statement.script_type == "stub" or statement.script_type == "static":
                compiled = compiled + statement.script_return_type + " "
            compiled = compiled + statement.script_name + compile_script(statement.children[0], beautify, level) + newline + "end"
            return compiled

        # Script block
        elif type == StatementType.SCRIPT_BLOCK:
            for c in statement.children:
                compiled = compiled + newline + generate_spaces(level + 1) + compile_script(c, beautify, level + 1)
            return compiled

        # Function call
        elif type == StatementType.FUNCTION_CALL:
            if statement.function_name == "set":
                format_string = "{:s} = {:s}" if beautify else "{:s}={:s}"
                return format_string.format(compile_script(statement.children[0], level), compile_script(statement.children[1], beautify, level))
            elif statement.function_name == "not":
                return "!{:s}".format(compile_script(statement.children[0], beautify, level))
            elif statement.function_name == "=" or statement.function_name in ARITHMETIC_SYMBOLS:
                function_name = statement.function_name
                if function_name == "=":
                    function_name = "=="
                format_string = "({:s} {:s} {:s})" if beautify or statement.function_name == "or" or statement.function_name == "and" else "({:s}{:s}{:s})"
                return format_string.format(compile_script(statement.children[0], beautify, level), function_name, compile_script(statement.children[1], beautify, level))

            compiled = statement.function_name + "("
            for c in range(len(statement.children)):
                compiled = compiled + compile_script(statement.children[c], beautify, level)
                if c + 1 < len(statement.children):
                    compiled = compiled + ", "
            return compiled + ")"

        # If statement
        elif type == StatementType.IF_STATEMENT:
            compiled = "if " + compile_script(statement.children[0], beautify, level)

            if len(statement.children) <= 3 and len(statement.children) > 1:
                compiled = compiled + compile_script(statement.children[1], beautify, level) + newline
                if len(statement.children) == 3:
                    compiled = compiled + generate_spaces(level) + "else" + compile_script(statement.children[2], beautify, level) + newline
            else:
                raise CompileError("invalid if statement")

            return compiled + generate_spaces(level) + "end"


        else:
            raise CompileError("{:s} is unimplemented".format(type))

def dont_generate_spaces(level):
    return ""

def do_generate_spaces(level):
    spaces = ""
    for i in range(level):
        spaces = spaces + "    "
    return spaces
