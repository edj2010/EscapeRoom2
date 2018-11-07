###
# CONSTANTS
###

INACTIVE = -1
ACTIVE = 0
FINISHED = 1

###
# PROVIDED FUNCTIONS
###

def AND(args):
    return len(list(filter(lambda x: x != FINISHED, args))) == 0

def OR(args):
    return len(list(filter(lambda x: x == FINISHED, args))) > 0

###
#
# Format instructions:
# each function takes in a list, and returns a bool
# the list is the statuses of all states the state in question depends on
# the output is a bool indicating whether to activate the state or not
#
###


###
# CUSTOM FUNCTIONS
###
