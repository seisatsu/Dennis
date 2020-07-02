#####################
# Dennis MUD        #
# redirect_exit.py  #
# Copyright 2020    #
# Michael D. Reiley #
#####################

# **********
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# **********

NAME = "redirect exit"
CATEGORIES = ["exits"]
USAGE = "redirect exit <id> <destination>"
DESCRIPTION = """Set the destination room of the exit <id> in the current room to <destination>.

The current room must not be outbound sealed, and the destination room must not be inbound sealed.
These restrictions do not apply to the owner of the current room and the owner of the destination room, respectively.
You must own the exit or its room.

Ex. `redirect exit 3 27` to redirect exit 3 to room 27."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=2):
        return False

    # Perform argument type checks and casts.
    exitid, destroomid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int], [1, int]], retargs=[0, 1])
    if exitid is None or destroomid is None:
        return False

    # Lookup the current room, and perform exit checks.
    thisroom = COMMON.check_exit(NAME, console, exitid)
    if not thisroom:
        return False

    # Lookup the destination room and perform room checks.
    destroom = COMMON.check_room(NAME, console, destroomid)
    if not destroom:
        return False

    # Make sure we own the exit or the current room, or we are a wizard.
    if console.user["name"] not in thisroom["exits"][exitid]["owners"] \
            and console.user["name"].lower() not in thisroom["owners"] and not console.user["wizard"]:
        console.msg("{0}: you do not own this exit or this room".format(NAME))
        return False

    # Make sure the current room is not outbound sealed, or we are a room owner or a wizard.
    if thisroom["sealed"]["outbound"] and not console.user["wizard"] and console.user["name"] not in thisroom["owners"]:
        console.msg("{0}: the current room is outbound sealed".format(NAME))
        return False

    # Make sure the destination room is not inbound sealed, or we are a room owner or a wizard.
    if destroom["sealed"]["inbound"] and not console.user["wizard"] and console.user["name"] not in destroom["owners"]:
        console.msg("{0}: the destination room is inbound sealed".format(NAME))
        return False

    # Redirect the exit.
    thisroom["exits"][exitid]["dest"] = destroomid
    console.database.upsert_room(thisroom)

    # Finished.
    console.msg("{0}: done".format(NAME))
    return True
