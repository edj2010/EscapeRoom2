import json
from sqlalchemy import create_engine, select
from collections import defaultdict
import serverlogic
from flask import Flask
from models import nodes_table, metadata
import datetime

app = Flask(__name__)


def heartbeatHandler(nodeName):
    """
    sets the last_ping value for a given node to the current time.
    This is used to track if any nodes become unresponsive
    """

    conn = pServer.engine.connect()
    stmt = (
        nodes_table.update()
        .where(nodes_table.c.client_id == pServer.nodes[nodeName])
        .values(last_ping=datetime.datetime.now())
    )
    conn.execute(stmt)


@app.route("/")
def welcome():
    """
    Generic landing screen
    """
    return "Welcome to our Escape Room."


@app.route("/input/<nodeName>/<value>")
def input(nodeName, value):
    """
    Given a node and a value, looks up the trigger that the node inputs to, and sends
    the value passed to the out_val for the trigger's output node
    """
    heartbeatHandler(nodeName)
    outputNodes = pServer.mappings[nodeName]
    for outputNode in outputNodes:
        if outputNode in pServer.nodes:
            conn = pServer.engine.connect()
            updtStmt = (
                nodes_table.update()
                .where(nodes_table.c.client_id == pServer.nodes[outputNode])
                .values(out_val=value)
            )
            conn.execute(updtStmt)
        else:
            raise KeyError("{0} is not a node".format(outputNode))
            # TODO: Change this to a http error code
    return "values set"


@app.route("/output/<nodeName>")
def output(nodeName):
    """Retrieves the out_val for a given node"""
    heartbeatHandler(nodeName)
    if nodeName in pServer.nodes:
        conn = pServer.engine.connect()
        selStmt = select([nodes_table]).where(nodes_table.c.client_name == nodeName)
        results = conn.execute(selStmt)
        return results.fetchone()["out_val"]
    else:
        raise KeyError("{0} is not a node".format(nodeName))
        # TODO: Change this to a http error code


@app.route("/streamStatus/<streamController>/<nodeName>")
def streamStatus(streamController, nodeName):
    """Checks whether a given stream is active or not"""
    heartbeatHandler(nodeName)
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
        self.nodes = {node: ID for ID, node in enumerate(connections["Nodes"])}
        self.streams = connections["Streams"]
        self.mappings = connections["Mappings"]
        self.outputs = defaultdict(str)
        self.localVals = {}
        self.engine = create_engine("sqlite:///server.db", echo=True)
        if not self.engine.dialect.has_table(self.engine, "nodes_table"):
            metadata.bind = self.engine
            metadata.create_all(self.engine)
            i = nodes_table.insert()
            for node in self.nodes:
                i.execute(
                    {
                        "client_id": self.nodes[node],
                        "client_name": node,
                        "last_ping": datetime.datetime.now(),
                        "out_val": "",
                    }
                )


pServer = PuzzleServer("connections.json")
