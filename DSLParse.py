"""
RemoteNode(PressurePlates)
LocalNode(JungleCounter)
RemoteNode(JungleLock)
Trigger(PressurePlates, JungleCounter)
Trigger(JungleCounter, JungleLock)

RemoteNode(Dial)
LocalNode(DialVal)
Stream(Dial, DialVal, JungleDial)

JSONIFY

{"LocalNodes": ["JungleCounter", "DialVal"],
 "RemoteNodes": ["PressurePlates", "JungleLock", "Dial"],
 "Streams": ["JungleDial"]
 "Mappings": {"PressurePlates": ["JungleCounter"],
              "JungleCounter": ["JungleLock"],
              "Dial": ["DialVal"]}
}


"""

DSLFILE = "connections.pzl"
JSONFILE = "connections.json"

from collections import defaultdict
import json


def main():
    DSLParse()


# parses dslfile and outputs to jsonfile
def DSLParse(dslfile=DSLFILE, jsonfile=JSONFILE):

    # read in dsl
    with open(dslfile, "r") as infile:
        dslLines = infile.readlines()

    # initialize json dictionary components
    jsonDict = dict()
    jsonDict["LocalNodes"] = list()
    jsonDict["RemoteNodes"] = list()
    jsonDict["Streams"] = list()
    jsonDict["Mappings"] = defaultdict(list)

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

        else:
            jsonDict[category + "s"].append(data[0])

    with open(jsonfile, "w") as outfile:
        json.dump(jsonDict, outfile)


main()
