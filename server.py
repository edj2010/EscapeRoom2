import json
from collections import defaultdict
import serverlogic
from flask import Flask

app = Flask(__name__)


@app.route("/")
def welcome():
    return "Welcome to our Escape Room."


@app.route("/input/<nodeName>/<value>")
def input(nodeName, value):
    outputNodes = pServer.mappings[nodeName]
    for outputNode in outputNodes:
        if outputNode in pServer.localNodes:
            nodeObj = getattr(serverlogic, outputNode)
            change, nodeValue = nodeObj.compute(value)
            if change:
                input(outputNode, nodeObj.value)
                pServer.localVals[outputNode] = nodeValue
                print("Set local val {0} to {1}".format(outputNode, nodeValue))
        elif outputNode in pServer.remoteNodes:
            pServer.outputs[outputNode] = value
        else:
            raise KeyError("{0} is not a local or remote node".format(outputNode))
            # TODO: Change this to a http error code
    return "values set"


@app.route("/output/<nodeName>")
def output(nodeName):
    if nodeName in pServer.remoteNodes:
        return str(pServer.outputs[nodeName])
    else:
        raise KeyError("{0} is not a remote node".format(nodeName))
        # TODO: Change this to a http error code


@app.route("/streamStatus/<streamController>")
def streamStatus(streamController):
    if streamController in pServer.streams:
        streamControllerObj = getattr(serverlogic, streamController)
        return str(streamControllerObj.isActive(pServer.localVals, None))
    else:
        raise KeyError("{0} is not a stream controller".format(streamController))
        # TODO: Change this to a http error code


class PuzzleServer:
    def __init__(self, filename):
        with open(filename, "r") as infile:
            connections = json.load(infile)
        self.localNodes = set(connections["LocalNodes"])
        self.remoteNodes = set(connections["RemoteNodes"])
        self.streams = connections["Streams"]
        self.mappings = connections["Mappings"]
        self.outputs = defaultdict(str)
        self.localVals = {}


pServer = PuzzleServer("connections.json")
