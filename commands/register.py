import hashlib
from datatype import User

NAME = "register"
USAGE = "register <username> <password>"
DESCRIPTION = "Register a new user with <username> and <password>."


def COMMAND(console, database, args):
    # args = [username, password]
    if len(args) != 2:
        console.msg("Usage: " + USAGE)
        return False

    # Register a new user.
    check = database.filter(
        User, {
            "name": args[0]
        }
    )
    if len(check) != 0:  # User already exists.
        console.msg(NAME + ": user already exists")
        return False

    # Create new user.
    newuser = User({
        "name": args[0],
        "nick": args[0],
        "desc": "",
        "passhash": hashlib.sha256(args[1].encode()).hexdigest(),
        "online": False,
        "room": 0,
        "inventory": [],
        "wizard": False
    })

    # Save.
    database.insert(newuser)
    console.msg("registered user \"" + args[0] + "\"")
    return True
