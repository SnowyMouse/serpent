#!/usr/bin/env python3
#
# parser/hsc_parser.py
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
from tokenizer import Token, TokenType, ARITHMETIC_SYMBOLS, EQUALITY_OPERATORS, RELATIONAL_OPERATORS, LOGICAL_OPERATORS
from .types import StatementType, ParserError, SCRIPT_TYPES, VALUE_TYPES, Statement

# Parse the HSC script
def parse(tokens):
    next_token = 0

    main_script = Statement()
    main_script.statement_type = StatementType.MAIN_SCRIPT_BLOCK
    main_script.children = []

    while next_token < len(tokens):
        token = tokens[next_token]

        # Make sure the next token is the beginning of something
        if token.token != "(":
            raise ParserError(token, "Unexpected token", "Token used here")

        # Make sure we have enough tokens to do something
        if next_token + 3 > len(tokens):
            raise ParserError(token, "Incomplete statement", "Beginning of statement here")

        token_after = tokens[next_token + 1]

        statement = None

        # Parse a global
        if token_after.token == "global":
            statement = parse_global(tokens, next_token)

        # Parse a script
        elif token_after.token == "script":
            statement = parse_script(tokens, next_token)

        # Die alone
        else:
            raise ParserError(token_after, "Unexpected token", "Token used here")

        main_script.children.append(statement)
        next_token = next_token + statement.token_count

    return main_script

def parse_global(tokens, next_token):
    if next_token + 6 > len(tokens):
        raise ParserError(tokens[next_token], "Incomplete global definition", "Global defined here")

    statement = Statement()
    statement.statement_type = StatementType.GLOBAL_DEFINITION

    # Make sure the name is valid
    global_name = tokens[next_token + 3]
    if global_name.token_type != TokenType.OTHER:
        raise ParserError(global_name, "Invalid global name {:s}".format(global_name.token), "Global name defined here")
    statement.global_name = global_name.token

    # Make sure the type is valid
    statement.global_type = tokens[next_token + 2].token
    if statement.global_type not in VALUE_TYPES:
        raise ParserError(tokens[next_token + 1], "Invalid global type {:s}".format(statement.global_type), "Global type defined here")

    # Parse the incoming expression
    expression = parse_expression(tokens, next_token + 4)
    statement.children = [expression]
    statement.token_count = 5 + expression.token_count

    return statement

def parse_script(tokens, next_token):
    if next_token + 6 > len(tokens):
        raise ParserError(tokens[next_token], "Incomplete script definition", "Script defined here")

    statement = Statement()
    statement.statement_type = StatementType.SCRIPT_DEFINITION
    first_token = next_token

    # Script type
    script_type = tokens[next_token + 2]
    if script_type.token not in SCRIPT_TYPES:
        raise ParserError(script_type, "Invalid script type {:s}".format(script_type.token), "Script type defined here")
    statement.script_type = script_type.token

    # Return type
    requires_type = script_type.token == "stub" or script_type.token == "static"

    if requires_type:
        if next_token + 7 > len(tokens):
            raise ParserError(tokens[next_token], "Incomplete script definition", "Script defined here")

        script_return_type = tokens[next_token + 3]
        if script_return_type.token not in VALUE_TYPES:
            raise ParserError(script_type, "Invalid script return type {:s}".format(script_return_type.token), "Script return type defined here")
        statement.script_return_type = script_return_type.token

    # Offset by 1 if a type is specified
    offset = 4 if requires_type else 3

    script_name = tokens[next_token + offset]
    if script_name.token_type != TokenType.OTHER:
        raise ParserError(global_name, "Invalid script name {:s}".format(script_name.token), "Script name defined here")
    statement.script_name = script_name.token

    next_token = next_token + offset + 1

    # Go through each token until finished
    objects = []
    exited_properly = False

    script_block = Statement()
    script_block.statement_type = StatementType.SCRIPT_BLOCK

    while next_token < len(tokens):
        token = tokens[next_token]
        if token.token == ")":
            exited_properly = True
            break
        else:
            expression = parse_expression(tokens, next_token)
            script_block.children.append(expression)
            next_token = next_token + expression.token_count

    # Make sure everything is all good
    if not exited_properly:
        raise ParserError(tokens[next_token - 1], "Incomplete script definition", "Expected `)` after here")

    statement.token_count = next_token - first_token + 1
    statement.children = [script_block]


    return statement


def parse_expression(tokens, next_token):
    statement = Statement()
    statement.statement_type = StatementType.EXPRESSION
    if tokens[next_token].token == "(":
        function_call = parse_function_call(tokens, next_token)
        statement.token_count = function_call.token_count
        statement.children = [function_call]
    else:
        statement.children = [tokens[next_token]]
        statement.token_count = 1
    return statement

# Parse function calls e.g. (function arg1 arg2)
def parse_function_call(tokens, next_token):
    statement = Statement()
    first_token = next_token
    statement.statement_type = StatementType.FUNCTION_CALL
    if next_token + 3 > len(tokens):
        raise ParserError(tokens[next_token], "Incomplete function call", "Function used here")

    # Get the function name
    function_name = tokens[next_token + 1]
    if function_name.token_type == "(":
        raise ParserError(function_name, "Unexpected token", "Token used here")
    statement.function_name = function_name.token

    next_token = next_token + 2
    exited_properly = False
    while next_token < len(tokens):
        token = tokens[next_token]
        if token.token == ")":
            exited_properly = True
            break
        else:
            expression = parse_expression(tokens, next_token)
            statement.children.append(expression.children[0])
            next_token = next_token + expression.token_count

    if not exited_properly:
        raise ParserError(tokens[next_token - 1], "Incomplete function call", "Expected `)` after here")

    statement.token_count = next_token - first_token + 1

    if statement.function_name == "begin":
        statement.statement_type = StatementType.SCRIPT_BLOCK
    elif statement.function_name == "if":
        statement.statement_type = StatementType.IF_STATEMENT
        num_children = len(statement.children)
        if num_children < 2 or num_children > 3:
            raise ParserError(tokens[first_token], "Invalid if statement", "If statement defined here")

        for i in range(num_children - 1):
            if statement.children[1 + i].statement_type != StatementType.SCRIPT_BLOCK:
                block = Statement()
                block.statement_type = StatementType.SCRIPT_BLOCK
                block.children = [statement.children[1 + i]]
                statement.children[1 + i] = block
    elif statement.function_name in ARITHMETIC_SYMBOLS or statement.function_name == "=" and len(statement.children) != 2:
        raise ParserError(tokens[first_token], "Invalid arithmetic function", "Expected exactly two parameters here")



    return statement
