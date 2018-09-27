NAME = "go"
USAGE = "go <exit>"
DESCRIPTION = "Take the exit called <exit> to wherever it may lead."


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Look for the current room.
    thisroom = database.room_by_id(console.user["room"])
    if not thisroom:
        console.msg("warning: current room does not exist")
        return False  # The current room does not exist?!

    exits = thisroom["exits"]
    if len(exits):
        for e in exits:
            if e["name"].lower() == ' '.join(args).lower():
                # Check if the destination room exists.
                destroom = database.room_by_id(e["dest"])
                if not destroom:
                    console.msg(NAME + ": destination room does not exist")
                    return False  # The destination room does not exist.

                # Move us to the new room.
                if console.user["name"] in thisroom["users"]:
                    thisroom["users"].remove(console.user["name"])
                if console.user["name"] not in destroom["users"]:
                    destroom["users"].append(console.user["name"])
                console.broadcast_room(console.user["nick"] + " left the room through " + e["name"])
                console.user["room"] = destroom["id"]
                console.broadcast_room(console.user["nick"] + " entered the room through " + e["name"])
                database.upsert_room(thisroom)
                database.upsert_room(destroom)
                database.upsert_user(console.user)
                console.msg("exited " + e["name"])
                console.command("look")
                return True

    console.msg(NAME + ": no such exit")
    return False
