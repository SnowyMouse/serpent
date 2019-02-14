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
from copy import copy
from error import warning, error, show_message_for_character
from enum import Enum
from tokenizer import Token, TokenType, ARITHMETIC_SYMBOLS, EQUALITY_OPERATORS, RELATIONAL_OPERATORS, LOGICAL_OPERATORS

# Statement types
class StatementType(Enum):
    MAIN_SCRIPT_BLOCK  = 0
    GLOBAL_DEFINITION  = 1
    SCRIPT_DEFINITION  = 2
    SCRIPT_BLOCK       = 3
    IF_STATEMENT       = 4
    EXPRESSION         = 5
    FUNCTION_CALL      = 6

# Parser error
class ParserError(Exception):
    token = None
    message = "An error occurred"
    message_under = "This is where it occurred"
    def __init__(self, token, message, message_under):
        self.token = token
        self.message = message
        self.message_under = message_under
    def __str__(self):
        return "ParserError: {:s}".format(self.message)

SCRIPT_TYPES = [
    "static",
    "dormant",
    "continuous",
    "stub",
    "startup"
]

VALUE_TYPES = [
    "void",
    "short",
    "long",
    "real",
    "boolean",
    "string",
    "trigger_volume",
    "cutscene_flag",
    "cutscene_camera_point",
    "cutscene_title",
    "cutscene_recording",
    "device_group",
    "ai",
    "ai_command_list",
    "starting_profile",
    "conversation",
    "navpoint",
    "hud_message",
    "object_list",
    "sound",
    "effect",
    "damage",
    "looping_sound",
    "animation_graph",
    "actor_variant",
    "damage_effect",
    "object_definition",
    "game_difficulty",
    "team",
    "ai_default_state",
    "actor_type",
    "hud_corner",
    "object",
    "unit",
    "vehicle",
    "weapon",
    "device",
    "scenery",
    "object_name",
    "unit_name",
    "vehicle_name",
    "weapon_name",
    "device_name",
    "scenery_name"
]

# Statement
class Statement:
    statement_type = None
    children = None

    # Number of tokens that was consumed for this
    token_count = None

    # If global
    global_type = None
    global_name = None

    # If function call
    function_name = None

    # If script
    script_name = None
    script_type = None
    script_return_type = None

    def __init__(self):
        self.children = []

# Parse the main script block
def parse(tokens):
    script = Statement()
    script.statement_type = StatementType.MAIN_SCRIPT_BLOCK

    # Go through each token
    token_count = len(tokens)
    next_token = 0
    while next_token < token_count:
        token = tokens[next_token]

        # Add a global?
        if token.token == "global":
            global_to_add = parse_global(tokens, next_token)
            script.children.append(global_to_add)
            next_token = next_token + global_to_add.token_count

        # Add a function?
        elif token.token in SCRIPT_TYPES:
            script_to_add = parse_script(tokens, next_token)
            script.children.append(script_to_add)
            next_token = next_token + script_to_add.token_count

        else:
            raise ParserError(token, "Unexpected token", "Token used here")

        #next_token = next_token + 1
    return script

# Add the global thingy!
def parse_global(tokens, next_token):
    statement = Statement()

    # Minimum tokens for a global statement (global, type, name)
    statement.token_count = 5
    statement.statement_type = StatementType.GLOBAL_DEFINITION

    # Make sure we have enough for that
    if(len(tokens) - next_token < 5):
        raise ParserError(tokens[next_token], "Incomplete global definition", "Global defined here")

    # Get the global type and name
    statement.global_type = tokens[next_token + 1].token
    global_name = tokens[next_token + 2]

    # Make sure it's a valid global type
    if statement.global_type not in VALUE_TYPES:
        raise ParserError(tokens[next_token + 1], "Invalid global type {:s}".format(statement.global_type), "Global type defined here")

    # Also make sure it's a valid global name
    if global_name.token_type != TokenType.OTHER:
        raise ParserError(tokens[next_token + 2], "Invalid global name {:s}".format(global_name.token), "Global name defined here")
    else:
        statement.global_name = global_name.token

    # Lastly, make sure the global is set to something
    if(tokens[next_token + 3].token == "="):
        statement.token_count = 4
        expression = parse_expression(tokens, next_token + statement.token_count)
        if expression.token_count == 0:
            raise ParserError(tokens[next_token], "Incomplete global definition", "Global defined here")

        statement.token_count = statement.token_count + expression.token_count
        statement.children = [expression]
    else:
        raise ParserError(tokens[next_token + 2], "Incomplete global definition", "Expected `=` after here")

    return statement

# Add the script thingy!
def parse_script(tokens, next_token):
    statement = Statement()

    statement.token_count = 3
    name_offset = 1
    statement.statement_type = StatementType.SCRIPT_DEFINITION

    # Set the script type to the first token
    statement.script_type = tokens[next_token].token

    # Statics and stubs require an additional return type
    if statement.script_type == "static" or statement.script_type == "stub":
        statement.token_count = 4
        name_offset = 2

    # Make sure we have enough for that
    if(len(tokens) - next_token < statement.token_count):
        raise ParserError(tokens[next_token], "Incomplete script definition", "Script defined here")

    # Get the return type
    if statement.script_type == "static" or statement.script_type == "stub":
        statement.script_return_type = tokens[next_token + 1].token
        if statement.script_return_type not in VALUE_TYPES:
            raise ParserError(tokens[next_token + 1], "Invalid return value type", "Type defined here")


    # Get the script name
    statement.script_name = tokens[next_token + name_offset].token

    # Start getting things
    next_token = next_token + name_offset + 1
    script_block = parse_block(tokens, next_token)
    statement.children.append(script_block)
    statement.token_count = statement.token_count + script_block.token_count

    return statement

# Add if statement
def parse_if_statement(tokens, next_token):
    statement = Statement()

    first_token = next_token

    statement.statement_type = StatementType.IF_STATEMENT

    incomplete_if_statement_error = "Incomplete if statement at {:d}:{:d}".format(tokens[first_token].line,tokens[first_token].character)

    if(next_token + 3 > len(tokens)):
        raise ParserError(tokens[next_token], incomplete_if_statement_error, "If statement defined here")

    # Get the condition
    condition = parse_expression(tokens, next_token + 1)
    statement.children.append(condition)
    next_token = next_token + 1 + condition.token_count

    # Get the first block (if true)
    first_block = parse_block(tokens, next_token, True)
    next_token = next_token + first_block.token_count
    statement.children.append(first_block)

    if next_token >= len(tokens) or (tokens[next_token].token != "end" and tokens[next_token].token != "else" and tokens[next_token].token != "elseif"):
        raise ParserError(tokens[next_token - 1], incomplete_if_statement_error, "Expected end or else after here")

    # Add else if we need it
    if tokens[next_token].token == "else" or tokens[next_token].token == "elseif":
        next_token = next_token + 1
        second_block = None

        # Elseif, consumes the elseif and end
        if tokens[next_token - 1].token == "elseif":
            # Go back one token to get the elseif, too
            next_token = next_token - 1

            second_block = parse_if_statement(tokens, next_token)

            # Subtract the elseif
            next_token = next_token + second_block.token_count - 1

        # Regular else
        else:
            second_block = parse_block(tokens, next_token, False)
            next_token = next_token + second_block.token_count


        statement.children.append(second_block)

        if next_token >= len(tokens):
            raise ParserError(tokens[next_token - 1], incomplete_if_statement_error, "Expected end after here")
        elif tokens[next_token].token != "end":
            raise ParserError(tokens[next_token], incomplete_if_statement_error, "Expected end here")

    statement.token_count = next_token - first_token + 1

    return statement

# Do script blocks
def parse_block(tokens, next_token, can_end_on_else = False):
    statement = Statement()
    statement.statement_type = StatementType.SCRIPT_BLOCK

    started_on = next_token
    ended_properly = False

    while next_token < len(tokens):
        token = tokens[next_token]
        if token.token_type == TokenType.OTHER:
            # See if we're ending
            if token.token == "end" or ((token.token == "else" or token.token == "elseif") and can_end_on_else):
                ended_properly = True
                break

            # If not, let's see what the next token is
            if next_token + 1 == len(tokens):
                raise ParserError(token, "Unknown token", "Expected more tokens after here")

            token_after = tokens[next_token + 1]

            # If statement!
            if token.token == "if":
                if_to_add = parse_if_statement(tokens, next_token)

                statement.children.append(if_to_add)
                next_token = next_token + if_to_add.token_count
                continue

            # Function call
            elif token_after.token == "(":
                function_call = parse_function_call(tokens, next_token)
                next_token = next_token + function_call.token_count
                statement.children.append(function_call)
                continue

            # Setting a globaL
            elif token_after.token == "=":
                expression = parse_expression(tokens, next_token + 2)
                if len(expression.children) == 0:
                    raise ParserError(token_after, "Expected non-empty expression", "Empty expression after here")

                set_function = Statement()
                set_function.statement_type = StatementType.FUNCTION_CALL
                set_function.function_name = "set"
                set_function.children = [token, expression]

                next_token = next_token + 2 + expression.token_count
                statement.children.append(set_function)
                continue

            # Who knows?
            else:
                raise ParserError(token_after, "Unexpected token", "Token used here")
        else:
            raise ParserError(token, "Unexpected token", "Token used here")

    # Make sure we ended properly
    if not ended_properly:
        message = "Expected end after here"
        if can_end_on_else:
            message = "Expected end or else after here"
        raise ParserError(tokens[next_token - 1], "Incomplete script block", message)

    statement.token_count = next_token - started_on

    return statement

# Add expression
# @param tokens      tokens array
# @param next_token  first token this expression is
# @param parenthesis starts and ends on parenthesis, consuming the parenthesis
# @param in_function end on comma or parenthesis, but does not consume the parenthesis or comma
# @return            whatever resulting statement comes out of this
def parse_expression(tokens, next_token, parenthesis = False, in_function = False):
    statement = Statement()
    statement.statement_type = StatementType.EXPRESSION
    last_token = next_token

    # If we're starting on parenthesis then add 1 to last_token, making sure there actually is a `(` there
    # If not, it's a programming error that should be fixed
    if parenthesis:
        assert last_token < len(tokens) and tokens[last_token].token == "("
        last_token = last_token + 1

    # Get everything in this expression
    parts = []

    class LastType(Enum):
        ARITHMETIC_OPERATOR = 1
        NON_SYMBOL = 2

    last_type = None
    while True:
        if last_token == len(tokens):
            if parenthesis:
                raise ParserError(tokens[last_token - 1], "Expected `)` in expression", "Expected after this")
            else:
                break

        token = copy(tokens[last_token])

        # If it's a symbol, maybe we can handle it?
        if token.token_type == TokenType.SYMBOL or token.token in LOGICAL_OPERATORS:
            # Add expressions in expressions, or a function
            if token.token == "(":
                if last_type == None or last_type == LastType.ARITHMETIC_OPERATOR:
                    part = parse_expression(tokens, last_token, True)
                    parts.append(part)

                    # Add last_token
                    last_token = last_token + part.token_count
                    last_type = LastType.NON_SYMBOL
                else:
                    function_call = parse_function_call(tokens, last_token - 1)
                    last_token = last_token + function_call.token_count - 1
                    del parts[-1]
                    parts.append(function_call)

            # Maybe we're terminating this?
            elif token.token == ")":
                if parenthesis:
                    last_token = last_token + 1
                    break
                elif in_function:
                    break
                else:
                    raise ParserError(token, "Unexpected right parenthesis", "Symbol used here")

            # Maybe we're terminating this (for a function)
            elif token.token == ",":
                if in_function:
                    break
                else:
                    raise ParserError(token, "Unexpected comma", "Symbol used here")

            # Arithmetic?
            elif token.token in ARITHMETIC_SYMBOLS or token.token == "+-" or token.token == "--":
                # We can't use an arithmetic operator unless there was something else that was not arithmetic before it
                if last_type != LastType.NON_SYMBOL:
                    raise ParserError(token, "Unexpected arithmetic operator", "Operator used here")

                # Simplify -- and +- to + and - respectively
                if(token.token == "--"):
                    token.token = "+"
                if(token.token == "+-"):
                    token.token = "-"

                # Add this token
                last_type = LastType.ARITHMETIC_OPERATOR
                parts.append(token)
                last_token = last_token + 1

            # Fail
            else:
                raise ParserError(token, "Unexpected whatever the hell that is", "Whatever the hell that is used here")

            continue

        # Maybe it's something else
        else:
            # If it's not a symbol, but the last one was a symbol, then the loop might be done?
            if last_type == LastType.NON_SYMBOL:
                # Unless it's a negative or positive number, which then it becomes subtraction/addition
                if token.token[0] == "-" or token.token[0] == "+":
                    token_sign = copy(token)
                    token_sign.token = token.token[0]
                    token_sign.token_type = TokenType.SYMBOL

                    token_copy = copy(token)
                    token_copy.token = token.token[1:]
                    token_copy.character = token_copy.character + 1

                    parts.append(token_sign)
                    parts.append(token_copy)
                    last_token = last_token + 1
                    last_type = LastType.NON_SYMBOL
                    continue

                # If we should be ending on a parenthesis, then it's a syntax error
                elif parenthesis or in_function:
                    raise ParserError(token, "Unexpected token in expression", "Token used here")
                else:
                    break

            # Maybe the expression is being cut too short by an end?
            elif token.token == "end" or token.token == "else" or token.token == "elseif":
                raise ParserError(token, "Unexpected end of block", "Token used here")
            else:
                parts.append(token)
                last_token = last_token + 1
                last_type = LastType.NON_SYMBOL
                continue

        last_token = last_token + 1

    # Check if we ended on an arithmetic operator
    if last_type == LastType.ARITHMETIC_OPERATOR:
        raise ParserError(parts[-1], "Expected operand for operator", "Operator used here")

    statement.token_count = last_token - next_token

    def parse_operator_functions(operators, parts):
        part_count = 0
        while part_count + 2 < len(parts):
            part = parts[part_count]
            next_part = parts[part_count + 1]
            next_part_after_that = parts[part_count + 2]

            if next_part.token in operators:
                new_statement = Statement()
                new_statement.statement_type = StatementType.FUNCTION_CALL
                new_statement.function_name = next_part.token

                if new_statement.function_name == "==":
                    new_statement.function_name = "="

                new_statement.children = [part, next_part_after_that]
                parts[part_count] = new_statement
                del parts[part_count + 1]
                del parts[part_count + 1]
            else:
                part_count = part_count + 2

    # Do each operator
    #
    # > Multiplication and division
    # > Addition and subtraction
    # > Relational (<, <=, >, >=)
    # > Equality (!=, ==)
    # > and
    # > or
    parse_operator_functions(["*", "/"], parts)
    parse_operator_functions(["+", "-"], parts)
    parse_operator_functions(RELATIONAL_OPERATORS, parts)
    parse_operator_functions(EQUALITY_OPERATORS, parts)
    parse_operator_functions(["and"], parts)
    parse_operator_functions(["or"], parts)

    statement.children = parts
    return statement

# Add a function
def parse_function_call(tokens, next_token):
    statement = Statement()
    statement.statement_type = StatementType.FUNCTION_CALL
    last_token = next_token + 2

    if next_token + 3 >= len(tokens):
        raise ParserError(tokens[next_token], "Invalid function call", "Expected function call here")

    statement.function_name = tokens[next_token].token
    if tokens[next_token + 1].token != "(":
        raise ParserError(tokens[next_token + 1], "Incomplete function call", "Expected left parenthesis here")

    # Loop through each possible token
    while True:
        if last_token == len(tokens):
            raise ParserError(tokens[last_token - 1], "Incomplete function call", "Expected right parenthesis after here")

        token = tokens[last_token]

        # Add the thing
        if token.token == ")":
            last_token = last_token + 1
            break

        # Skip this if it's a comma
        elif token.token == ",":
            raise ParserError(tokens[last_token], "Unexpected comma", "Expected expression or right parenthesis here")

        # Add it if it's an expression
        else:
            expression = parse_expression(tokens, last_token, False, True)
            last_token = last_token + expression.token_count
            statement.children.append(expression)
            if last_token < len(tokens) and tokens[last_token].token == ",":
                last_token = last_token + 1

    statement.token_count = last_token - next_token

    return statement
