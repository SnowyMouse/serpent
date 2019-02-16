#!/usr/bin/env python3
#
# parser/types.py
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
# Statement types

from enum import Enum

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
