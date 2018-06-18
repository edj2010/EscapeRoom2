import json
from sqlalchemy import create_engine
from collections import defaultdict
import serverlogic
from flask import Flask
from db import heartbeats
import datetime

app = Flask(__name__)

DB_EXISTS = True

@app.route("/")
def welcome():
    return "Welcome to our Escape Room."


@app.route("/input/<nodeName>/<value>")
def input(nodeName, value):
    conn = pServer.engine.connect()        
    stmt = heartbeats.update().where(heartbeats.c.client_name == nodeName).values(last_ping = datetime.datetime.now())
    conn.execute(stmt)
    outputNodes = pServer.mappings[nodeName]
    for outputNode in outputNodes:
        if outputNode in pServer.nodes:
            pServer.outputs[outputNode] = value
        else:
            raise KeyError("{0} is not a node".format(outputNode))
            # TODO: Change this to a http error code
    return "values set"


@app.route("/output/<nodeName>")
def output(nodeName):
    if nodeName in pServer.nodes:
        return str(pServer.outputs[nodeName])
    else:
        raise KeyError("{0} is not a node".format(nodeName))
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
        self.nodes = set(connections["Nodes"])
        self.streams = connections["Streams"]
        self.mappings = connections["Mappings"]
        self.outputs = defaultdict(str)
        self.localVals = {}
        self.engine = create_engine('sqlite:///server.db', echo=True)
        if not DB_EXISTS:
            i = heartbeat.insert()
            for ind, node in enumerate(self.nodes):
                i.execute({'client_id': ind, 'client_name': node, 'last_ping': datetime.datetime.now()})


pServer = PuzzleServer("connections.json")
