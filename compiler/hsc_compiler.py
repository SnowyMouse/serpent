#!/usr/bin/env python3
#
# compiler/hsc_compiler.py
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

from tokenizer import Token, TokenType
from parser import Statement, StatementType
from .types import CompileError, do_generate_spaces, dont_generate_spaces

# Translate a statement tree or token into its HSC equivalent
def compile_script(statement, strip = False, level = 0):
    if isinstance(statement, Token):
        quotes_can_be_removed = False

        if strip and statement.token_type == TokenType.STRING and len(statement.token[1:-1]) > 0:
            quotes_can_be_removed = True
            for c in statement.token[1:-1]:
                if not c.isalnum() and c != "_":
                    quotes_can_be_removed = False
                    break

        if quotes_can_be_removed:
            return statement.token[1:-1]
        else:
            return statement.token
    else:
        type = statement.statement_type

        newline = "" if strip else "\n"
        generate_spaces = dont_generate_spaces if strip else do_generate_spaces

        # Main script block
        if type == StatementType.MAIN_SCRIPT_BLOCK:
            compiled = ""
            for child in statement.children:
                compiled = compiled + compile_script(child, strip, level) + newline
            return compiled

        # Global
        elif type == StatementType.GLOBAL_DEFINITION:
            compiled = "(global {:s} {:s}".format(statement.global_type, statement.global_name)
            if len(statement.children) == 1:
                compiled = compiled + " " + compile_script(statement.children[0], strip, level)
            compiled = compiled + ")"
            return compiled

        # Expression
        elif type == StatementType.EXPRESSION:
            if len(statement.children) != 1:
                raise CompileError("invalid expression")
            return compile_script(statement.children[0], strip, level)

        # Function call
        elif type == StatementType.FUNCTION_CALL:
            compiled = "({:s}".format(statement.function_name)
            for child in statement.children:
                # Add an extra space IF needed
                if compiled[-1] != ")" or not strip:
                    compiled = compiled + " "
                compiled = compiled + compile_script(child, strip, level)
            compiled = compiled + ")"
            return compiled

        # Function definition
        elif type == StatementType.SCRIPT_DEFINITION:
            compiled = "(script {:s} ".format(statement.script_type)
            if statement.script_type == "static" or statement.script_type == "stub":
                compiled = compiled + statement.script_return_type + " "
            compiled = compiled + statement.script_name

            # For empty scripts, add something that does nothing. Otherwise, add the stuff it does
            if len(statement.children) == 0:
                compiled = compiled + " (+ 0 0)"
            else:
                for child in statement.children:
                    compiled = compiled + " " + compile_script(child, strip, level)

            compiled = compiled + (newline if len(statement.children) > 0 else "") + ")"
            return compiled

        # Script blocks
        elif type == StatementType.SCRIPT_BLOCK:
            compiled = ""
            if len(statement.children) == 0:
                compiled = "(+ 0 0)"
            else:
                for child in statement.children:
                    compiled = compiled + newline + generate_spaces(level + 1) + compile_script(child, strip, level + 1)
            return compiled

        # If statement
        elif type == StatementType.IF_STATEMENT:
            compiled = "(if"

            if len(statement.children) != 2 and len(statement.children) != 3:
                raise CompileError("invalid if statement")

            # Condition
            compiled = compiled + " " + compile_script(statement.children[0], strip, level)

            # Add an extra space IF needed
            if compiled[-1] != ")" or not strip:
                compiled = compiled + " "

            # if is true
            if len(statement.children[1].children) <= 1 or (isinstance(statement.children[1], Statement) and statement.children[1].statement_type == StatementType.IF_STATEMENT):
                compiled = compiled + compile_script(statement.children[1], strip, level)
            else:
                compiled = compiled + "(begin " + compile_script(statement.children[1], strip, level) + ")"

            # else
            if(len(statement.children) == 3):
                if len(statement.children[2].children) <= 1 or (isinstance(statement.children[2], Statement) and statement.children[2].statement_type == StatementType.IF_STATEMENT):
                    compiled = compiled + compile_script(statement.children[2], strip, level)
                else:
                    compiled = compiled + "(begin " + compile_script(statement.children[2], strip, level) + ")"

            compiled = compiled + newline + generate_spaces(level) + ")"

            return compiled

        else:
            raise CompileError("unimplemented")
