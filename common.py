#####################
# Dennis MUD        #
# common.py         #
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

# This module contains code for various tasks that need to be performed by commands fairly often.
# It is imported globally as COMMON.

from tinydb.table import Document


def check(NAME, console, args, argc=None, argmin=None, argmax=None, online=True, wizard=False,
          usage=True, reason=True):
    """Perform simple checks.

    :param NAME: The NAME field from the command module.
    :param console: The calling user's console.
    :param args: The args passed to the command.
    :param argc: The arg count to enforce.
    :param argmin: The arg count minimum to enforce.
    :param argmax: The arg count maximum to enforce.
    :param online: Whether to check if the user is online. Defaults to True.
    :param wizard: Whether to check if the user is a wizard.
    :param usage: Whether to show usage for the command if the check fails. Defaults to True.
    :param reason: Whether to show a common failure explanation if the check fails. Defaults to True.

    :return: True if succeeded, False if failed.
    """
    # Make sure we didn't receive argc along with argmin or argmax, because that would be pointless.
    if argc is not None and (argmin is not None or argmax is not None):
        console.log.error("received argc along with argmin or argmax in COMMON.check from command: {name}",
                          name=NAME)
        console.msg("{0}: internal command error".format(NAME))
        return None

    # Check argument count, if given.
    if argc is None:
        pass

    # If argc is not an int, report a type mismatch and fail.
    elif type(argc) is not int:
        console.log.error("argc type mismatch in COMMON.check from command: {name}", name=NAME)
        console.msg("{0}: internal command error".format(NAME))
        return None

    # The command received the wrong number of arguments. Fail.
    elif len(args) != argc:
        if usage:
            console.msg("Usage: {0}".format(console.shell._commands[NAME].USAGE))
        return False

    # Check argument minimum, if given.
    if argmin is None:
        pass

    # If argmin is not an int, report a type mismatch and fail.
    elif type(argmin) is not int:
        console.log.error("argc type mismatch in COMMON.check from command: {name}", name=NAME)
        console.msg("{0}: internal command error".format(NAME))
        return None

    # The command received too few arguments. Fail.
    elif len(args) < argmin:
        if usage:
            console.msg("Usage: {0}".format(console.shell._commands[NAME].USAGE))
        return False

    # Check argument maximum, if given.
    if argmax is None:
        pass

    # If argmax is not an int, report a type mismatch and fail.
    elif type(argmax) is not int:
        console.log.error("argc type mismatch in COMMON.check from command: {name}", name=NAME)
        console.msg("{0}: internal command error".format(NAME))
        return None

    # The command received too many arguments. Fail.
    elif len(args) > argmax:
        if usage:
            console.msg("Usage: {0}".format(console.shell._commands[NAME].USAGE))
        return False

    # Check if the calling user is logged in. Otherwise, fail.
    if online:
        if not console.user:
            if reason:
                console.msg("{0}: must be logged in first".format(NAME))
            return False

    # Check if the calling user is a wizard. Otherwise, fail.
    if wizard:
        if not console.user["wizard"]:
            if reason:
                console.msg("{0}: you do not have permission to use this command".format(NAME))
            return False

    # All checks succeeded.
    return True


def check_argtypes(NAME, console, args, checks, retargs=None, cast=True, usage=True):
    """Perform checks on the types of args passed to a command.

    :param NAME: The NAME field from the command module.
    :param console: The calling user's console.
    :param args: The args passed to the command.
    :param checks: A list or tuple of pairs in the form ((arg_index, expected_type)...).
    :param retargs: If set, an int, list, or tuple of arg index(es) to return from the original args on success.
    :param cast: Whether to cast the argument if returning it.
    :param usage: Whether to show usage for the command if the check fails.

    :return: True or args if succeeded, None if failed.
    """
    # Copy the command arguments for later in case we need to return typecasted copies.
    castargs = args.copy()

    # Make sure checks is a list or tuple. Otherwise report a type mismatch and fail.
    if type(checks) not in (list, tuple):
        console.log.error("checks type mismatch in COMMON.check_argtypes from command: {name}", name=NAME)
        console.msg("{0}: internal command error".format(NAME))
        return None

    # Investigate and perform checks.
    for chk in checks:
        # Each check should be a list or tuple of length 2. Fail.
        if type(chk) not in (list, tuple) or len(chk) != 2:
            console.log.error("checks member type mismatch in COMMON.check_argtypes from command: {name}", name=NAME)
            console.msg("{0}: internal command error".format(NAME))
            return None

        # The check indices can't be larger than length of the list of arguments to check. Fail.
        if chk[0] >= len(args):
            console.log.error("checks index mismatch in COMMON.check_argtypes from command: {name}", name=NAME)
            console.msg("{0}: internal command error".format(NAME))
            return None

        # Try to cast the arg at the given index as the given type.
        try:
            castargs[chk[0]] = chk[1](args[chk[0]])

        # Assume that the command was used incorrectly and give usage. Fail.
        except ValueError:
            if usage:
                console.msg("Usage: {0}".format(console.shell._commands[NAME].USAGE))
            return None

    # If we are not trying to return any arguments, skip these checks.
    if retargs is None:
        pass

    # We are returning a single argument.
    elif type(retargs) is int:
        # The retargs index can't be larger than length of the list of arguments to return. Fail.
        if retargs >= len(args):
            console.log.error("retargs index mismatch in COMMON.check_argtypes from command: {name}", name=NAME)
            console.msg("{0}: internal command error".format(NAME))
            return None

        # We are returning a typecasted argument.
        if cast:
            return castargs[retargs]

        # We are returning an uncasted argument.
        return args[retargs]

    # We are returning several arguments.
    elif type(retargs) in (list, tuple):
        retval = []
        # The retargs indices can't be larger than length of the list of arguments to return. Fail.
        for ret in retargs:
            if ret >= len(args):
                console.log.error("retargs index mismatch in COMMON.check_argtypes from command: {name}", name=NAME)
                console.msg("{0}: internal command error".format(NAME))
                return None

            # We are returning typecasted arguments.
            if cast:
                retval.append(castargs[ret])

            # We are returning uncasted arguments.
            else:
                retval.append(args[ret])

        # Return the argument(s) that were chosen.
        return retval

    # Something illegal was done with the retargs argument to this function. Fail.
    else:
        console.log.error("retargs type mismatch in COMMON.check_argtypes from command: {name}", name=NAME)
        console.msg("{0}: internal command error".format(NAME))
        return None

    # All checks succeeded.
    return True


def check_exit(NAME, console, exitid, room=None, owner=None, orwizard=True, reason=True):
    """Check if an exit exists in a room.
    
    For convenience, also checks the room and returns the room document if the room was found.

    :param NAME: The NAME field from the command module.
    :param console: The calling user's console.
    :param exitid: The exit id of the exit to check.
    :param room: The room id or room document of the room to check if set, otherwise check the user's current room.
    :param owner: If True, check the calling user for ownership. If a string, check the named user for ownership.
    :param orwizard: Whether to treat wizards as having ownership during ownership checks. Defaults to true.
    :param reason: Whether to show a common failure explanation if the check fails. Defaults to True.
    
    :return: Room document if succeeded, None if failed.
    """
    # Make sure exitid is an int. Otherwise report a type mismatch and fail.
    try:
        exitid = int(exitid)
    except ValueError:
        console.log.error("exitid type mismatch in COMMON.check_exit from command: {name}", name=NAME)
        console.msg("{0}: internal command error".format(NAME))
        return None

    # If the room argument is None, lookup the calling user's current room.
    if room is None:
        thisroom = console.database.room_by_id(console.user["room"])

    # If the room argument is an int, lookup the room with that ID.
    elif type(room) is int:
        thisroom = console.database.room_by_id(room)

    # If the room argument is a room document, use that.
    elif type(room) is Document:
        thisroom = room

    # An illegal type was passed to the room argument of this function. Fail.
    else:
        console.log.error("room type mismatch in COMMON.check_exit from command: {name}", name=NAME)
        console.msg("{0}: internal command error".format(NAME))
        return None

    # We couldn't find the room. Fail.
    if not thisroom:
        # What's more, the room we couldn't find was the user's current room. Double Fail.
        if room is None:
            console.log.error("current room does not exist for user: {user} ({room})", user=console.user["name"],
                              room=console.user["room"])
            console.msg("{0}: error: current room does not exist".format(NAME))

        # Always give this error if the room doesn't exist.
        console.log.error("nonexistent room in COMMON.check_exit from command: {name}", name=NAME)

        # Optionally throw a failure reason to the player.
        if reason:
            console.msg("{0}: no such exit".format(NAME))
        return None

    # We found the room but not the exit. Fail.
    elif exitid > len(thisroom["exits"]) - 1 or exitid < 0:
        if reason:
            console.msg("{0}: no such exit".format(NAME))
        return None

    # Perform a permission check on the current user.
    if owner is True:
        # Make sure the user owns the room or the exit. If so, pass along.
        if console.user["name"] in thisroom["owners"] or console.user["name"] in thisroom["exits"][exitid]["owners"]:
            pass

        # Optionally, check if the user is a wizard instead. If so, pass along.
        elif orwizard and console.user["wizard"]:
            pass

        # The user does not have permission for this exit or this room. Fail.
        else:
            if reason:
                console.msg("{0}: you do not own this exit or this room".format(NAME))
            return None

    # Perform a permission check on a named user.
    elif type(owner) is str:
        # Look up the named user and make sure they exist.
        targetuser = console.database.user_by_name(owner.lower())

        # The named user does not exist. Fail.
        if not targetuser:
            if reason:
                console.msg("{0}: no such user".format(NAME))
            return None

        # Make sure the user owns the room or the exit. If so, pass along.
        if targetuser["name"] in thisroom["owners"] or targetuser["name"] in thisroom["exits"][exitid]["owners"]:
            pass

        # Optionally, check if the user is a wizard instead. If so, pass along.
        elif orwizard and targetuser["wizard"]:
            pass

        # The user does not have permission for this exit or this room. Fail.
        else:
            if reason:
                console.msg("{0}: you do not own this exit or this room".format(NAME))
            return None

    # All checks succeeded. Return the room containing the exit as a convenience.
    return thisroom


def check_item(NAME, console, itemid, owner=None, holding=False, orwizard=True, reason=True):
    """Check if an item exists. If so, return it.

    :param NAME: The NAME field from the command module.
    :param console: The calling user's console.
    :param itemid: The item id of the item to check.
    :param owner: If True, check the calling user for ownership. If a string, check the named user for ownership.
    :param holding: Whether to check if the calling user is holding the item or is a wizard.
    :param orwizard: Whether to treat wizards as having ownership during ownership checks. Defaults to true.
    :param reason: Whether to show a common failure explanation if the check fails. Defaults to True.

    :return: Item document if succeeded, None if failed.
    """
    # Make sure itemid is an int. Otherwise report a type mismatch and fail.
    try:
        itemid = int(itemid)
    except ValueError:
        console.log.error("itemid type mismatch in COMMON.check_item from command: {name}", name=NAME)
        console.msg("{0}: internal command error".format(NAME))
        return None

    # Look up the target item.
    targetitem = console.database.item_by_id(itemid)

    # We couldn't find the item. Fail.
    if not targetitem:
        if reason:
            console.msg("{0}: no such item".format(NAME))
        return None

    # Check if the calling user is holding the item.
    if holding:
        # They are not holding the item, and they aren't a wizard who can twiddle items remotely. Fail.
        if itemid not in console.user["inventory"] and not console.user["wizard"]:
            if reason:
                console.msg("{0}: not holding item".format(NAME))
            return None

    # Perform a permission check on the current user.
    if owner is True:
        # Make sure the user owns the item. If so, pass along.
        if console.user["name"] in targetitem["owners"]:
            pass

        # Optionally, check if the user is a wizard instead. If so, pass along.
        elif orwizard and console.user["wizard"]:
            pass

        # The user does not have permission for this item. Fail.
        else:
            if reason:
                console.msg("{0}: you do not own this item".format(NAME))
            return None

    # Perform a permission check on a named user.
    elif type(owner) is str:
        # Look up the named user and make sure they exist.
        targetuser = console.database.user_by_name(owner.lower())

        # The named user does not exist. Fail.
        if not targetuser:
            if reason:
                console.msg("{0}: no such user".format(NAME))
            return None

        # Make sure the user owns the item. If so, pass along.
        if targetuser["name"] in targetitem["owners"]:
            pass

        # Optionally, check if the user is a wizard instead. If so, pass along.
        elif orwizard and targetuser["wizard"]:
            pass

        # The user does not have permission for this item. Fail.
        else:
            if reason:
                console.msg("{0}: you do not own this item".format(NAME))
            return None

    # All checks succeeded. Return the item.
    return targetitem


def check_room(NAME, console, roomid=None, owner=None, orwizard=True, reason=True):
    """Check if a room exists. If so, return it.

    :param NAME: The NAME field from the command module.
    :param console: The calling user's console.
    :param roomid: The room id of the room to check if set, otherwise check the user's current room.
    :param owner: If True, check the calling user for ownership. If a string, check the named user for ownership.
    :param orwizard: Whether to treat wizards as having ownership during ownership checks. Defaults to true.
    :param reason: Whether to show a common failure explanation if the check fails. Defaults to True.

    :return: Room document if succeeded, None if failed.
    """
    # If no room was given, use the current user's room.
    if roomid is None:
        roomid = console.user["room"]
    else:
        # Make sure roomid is an int. Otherwise report a type mismatch and fail.
        try:
            roomid = int(roomid)
        except ValueError:
            console.log.error("roomid type mismatch in COMMON.check_room from command: {name}", name=NAME)
            console.msg("{0}: internal command error".format(NAME))
            return None

    # Look up the target room.
    targetroom = console.database.room_by_id(roomid)

    # We couldn't find the room. Fail.
    if not targetroom:
        # What's more, the room we couldn't find was the user's current room. Double Fail.
        if roomid is None:
            console.log.error("current room does not exist for user: {user} ({room})", user=console.user["name"],
                              room=console.user["room"])
            console.msg("{0}: error: current room does not exist".format(NAME))
            return None

        # Optionally throw a failure reason to the player.
        elif reason:
            console.msg("{0}: no such room".format(NAME))
        return None

    # Perform a permission check on the current user.
    if owner is True:
        # Make sure the user owns the room. If so, pass along.
        if console.user["name"] in targetroom["owners"]:
            pass

        # Optionally, check if the user is a wizard instead. If so, pass along.
        elif orwizard and console.user["wizard"]:
            pass

        # The user does not have permission for this room. Fail.
        else:
            if reason:
                console.msg("{0}: you do not own this room".format(NAME))
            return None

    # Perform a permission check on a named user.
    elif type(owner) is str:
        # Look up the named user and make sure they exist.
        targetuser = console.database.user_by_name(owner.lower())

        # The named user does not exist. Fail.
        if not targetuser:
            if reason:
                console.msg("{0}: no such user".format(NAME))
            return None

        # Make sure the user owns the room. If so, pass along.
        if targetuser["name"] in targetroom["owners"]:
            pass

        # Optionally, check if the user is a wizard instead. If so, pass along.
        elif orwizard and targetuser["wizard"]:
            pass

        # The user does not have permission for this room. Fail.
        else:
            if reason:
                console.msg("{0}: you do not own this room".format(NAME))
            return None

    # All checks succeeded. Return the room.
    return targetroom


def check_user(NAME, console, username, online=False, wizard=None, live=False, reason=True, already=False):
    """Check if a user exists. If so, return it.

    :param NAME: The NAME field from the command module.
    :param console: The calling user's console.
    :param username: The username of the user to check.
    :param online: Whether to check if the user is online.
    :param wizard: If True, check if the user is a wizard. If False, check if the user is not a wizard.
    :param live: Whether to try to grab the live copy of the user document instead of pulling from the database.
    :param reason: Whether to show a common failure explanation if the check fails. Defaults to True.
    :param already: Whether to include the word "already" in the wizard failure explanation.

    :return: User document if succeeded, None if failed.
    """
    # Make sure roomid is a str. Otherwise report a type mismatch and fail.
    if type(username) is not str:
        console.log.error("username type mismatch in COMMON.check_user from command: {name}", name=NAME)
        console.msg("{0}: internal command error".format(NAME))
        return None

    # Look up the target user.
    username = username.lower()

    # If we need to modify the user's live data, try to request the copy of the user document from the shell.
    # If the user isn't online, this will just grab from the database.
    # Otherwise, request the user document from the database to begin with.
    if live:
        targetuser = console.shell.user_by_name(username)
    else:
        targetuser = console.database.user_by_name(username)

    # We couldn't find the user. Fail.
    if not targetuser:
        if reason:
            console.msg("{0}: no such user".format(NAME))
        return None

    # The user isn't online and we want them to be. Fail.
    elif online and not console.database.online(username):
        if reason:
            console.msg("{0}: user is not online".format(NAME))
        return None

    # Check the wizardship of the user.
    elif wizard is not None:
        # We want the user to be a wizard and they are not. Fail.
        if wizard and not targetuser["wizard"]:
            # Optionally choose between one of two failure reasons to throw to the player.
            if reason:
                if already:
                    console.msg("{0}: user is already not a wizard".format(NAME))
                else:
                    console.msg("{0}: user is not a wizard".format(NAME))
            return None

        # We want the user to not be a wizard and they are. Fail.
        elif targetuser["wizard"] and not wizard:
            # Optionally choose between one of two failure reasons to throw to the player.
            if reason:
                if already:
                    console.msg("{0}: user is already a wizard".format(NAME))
                else:
                    console.msg("{0}: user is a wizard".format(NAME))
            return None

    # All checks succeeded. Return the user.
    return targetuser