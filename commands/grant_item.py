NAME = "grant item"
USAGE = "grant item <id> <username>"
DESCRIPTION = "Add user <username> to the owners of item <id>."


def COMMAND(console, database, args):
    if len(args) != 2:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    try:
        itemid = int(args[0])
    except ValueError:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are holding the item.
    if itemid not in console.user["inventory"] and not console.user["wizard"]:
        console.msg(NAME + ": no such item in inventory")
        return False

    i = database.item_by_id(itemid)

    # Make sure we are the item's owner.
    if console.user["name"] not in i["owners"] and not console.user["wizard"]:
        console.msg(NAME + ": you do not own this item")
        return False

    u = database.user_by_name(args[1].lower())
    if not u:
        console.msg(NAME + ": no such user")
        return False

    # Check if the named user is already an owner.
    if args[1].lower() in i["owners"]:
        console.msg(NAME + ": user already an owner of this item")

    i["owners"].append(args[1].lower())
    database.upsert_item(i)
    console.msg(NAME + ": done")
    return True