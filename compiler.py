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

from tokenizer import Token, TokenType
from parser import Statement, StatementType

def CompileException(Exception):
    what = None
    def __main__(self, what):
        self.what = what

# Translate a statement tree or token into its HSC equivalent
def compile_script(statement):
    if isinstance(statement, Token):
        if statement.token_type == TokenType.STRING and " " not in statement.token:
            return statement.token[1:-1]
        else:
            return statement.token
    else:
        type = statement.statement_type

        # Main script block
        if type == StatementType.MAIN_SCRIPT_BLOCK:
            compiled = ""
            for child in statement.children:
                compiled = compiled + compile_script(child)
            return compiled

        # Global
        elif type == StatementType.GLOBAL_DEFINITION:
            compiled = "(global {:s} {:s}".format(statement.global_type, statement.global_name)
            if len(statement.children) == 1:
                compiled = compiled + " " + compile_script(statement.children[0])
            compiled = compiled + ")"
            return compiled

        # Expression
        elif type == StatementType.EXPRESSION:
            return compile_script(statement.children[0])

        # Function call
        elif type == StatementType.FUNCTION_CALL:
            compiled = "({:s}".format(statement.function_name)
            for child in statement.children:
                # Add an extra space IF needed
                if compiled[-1] != ")":
                    compiled = compiled + " "
                compiled = compiled + compile_script(child)
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
                    compiled = compiled + " " + compile_script(child)

            compiled = compiled + ")"
            return compiled

        # Script blocks
        elif type == StatementType.SCRIPT_BLOCK:
            compiled = ""
            if len(statement.children) == 0:
                compiled = "(+ 0 0)"
            else:
                for child in statement.children:
                    compiled = compiled + compile_script(child)
            return compiled

        # If statement
        elif type == StatementType.IF_STATEMENT:
            compiled = "(if"

            if len(statement.children) != 2 and len(statement.children) != 3:
                print("If statement doesn't have the right number of children", file=sys.stderr)
                raise CompileException("invalid if statement")

            # Condition
            compiled = compiled + " " + compile_script(statement.children[0])

            # Add an extra space IF needed
            if compiled[-1] != ")":
                compiled = compiled + " "

            # if is true
            if len(statement.children[1].children) <= 1 or (isinstance(statement.children[1], Statement) and statement.children[1].statement_type == StatementType.IF_STATEMENT):
                compiled = compiled + compile_script(statement.children[1])
            else:
                compiled = compiled + "(begin " + compile_script(statement.children[1]) + ")"

            # else
            if(len(statement.children) == 3):
                if len(statement.children[2].children) <= 1 or (isinstance(statement.children[2], Statement) and statement.children[2].statement_type == StatementType.IF_STATEMENT):
                    compiled = compiled + compile_script(statement.children[2])
                else:
                    compiled = compiled + "(begin " + compile_script(statement.children[2]) + ")"

            compiled = compiled + ")"

            return compiled

        else:
            print("I don't know what {:s} is".format(str(type)), file=sys.stderr)
            raise CompileException("unimplemented")
