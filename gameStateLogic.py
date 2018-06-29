###
# PROVIDED FUNCTIONS
###

def AND(*argv):
    return len(filter(lambda x: x!=1, *argv)) == 0

def OR(*argv):
    return len(filter(lambda x: x==1, *argv)) > 0
