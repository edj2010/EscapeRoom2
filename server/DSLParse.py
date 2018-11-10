
DSLFILE = "connections.pzl"
JSONFILE = "connections.json"

from collections import defaultdict
import json


def main():
    try:
        DSLParse()
    except:
        print("Formatting Error in " + DSLFILE + ". parsing terminated, failed to create " + JSONFILE)
        #TODO create more descriptive error message for identifying erroring line

# parses dslfile and outputs to jsonfile
def DSLParse(dslfile=DSLFILE, jsonfile=JSONFILE):

    # read in dsl
    with open(dslfile, "r") as infile:
        dslLines = infile.readlines()

    # initialize json dictionary components
    jsonDict = dict()
    jsonDict["Nodes"] = list()
    jsonDict["Streams"] = list()
    jsonDict["Mappings"] = defaultdict(list)
    jsonDict["States"] = ["Begin", "End"]
    jsonDict["Dependants"] = defaultdict(list)
    jsonDict["Dependancies"] = defaultdict(list)
    
    
    # parses each line of dslLines
    for line in dslLines:

        if "(" not in line:
            continue

        category, data = line.split("(")

        data = (data[:-2]).split(", ")

        if category == "Stream":
            jsonDict["Streams"].append(data[2])

        if category == "Stream" or category == "Trigger":
            jsonDict["Mappings"][data[0]].append(data[1])

        if category == "Node":
            jsonDict["Nodes"].append(data[0])

        if category == "State":
            jsonDict["States"].append(data[0])

        if category == "Dependancy":
            if len(data) == 2:
                jsonDict["Dependancies"][data[0]] = ["AND", data[1]]
                jsonDict["Dependants"][data[1]].append(data[0])
            else:
                jsonDict["Dependancies"][data[0]] = data[1:]
                for inputState in data[2:]:
                    jsonDict["Dependants"][inputState].append(data[0])
    jsonDict["Dependants"]["End"] = []

    with open(jsonfile, "w") as outfile:
        json.dump(jsonDict, outfile)

# Only have one of these uncommented at a time
# for standard use have main() uncommented
# for debugging, have DSLParse() uncommented
#main()
DSLParse()
