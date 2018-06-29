import json
from sqlalchemy import create_engine, select
from collections import defaultdict
import serverlogic
import gameStateLogic
from flask import Flask
from models import game_state_table, nodes_table, metadata
import datetime

app = Flask(__name__)

# Game State constants
INACTIVE = -1
ACTIVE = 0
FINISHED = 1
INACTIVE_COLOR = "grey73"
ACTIVE_COLOR = "yellow"
FINISHED_COLOR = "green"
ERROR_COLOR = "red"
FUNC_COLOR = "navy"

def heartbeatHandler(nodeName):
    """
    sets the last_ping value for a given node to the current time.
    This is used to track if any nodes become unresponsive
    """
    if nodeName in pServer.nodes:
        conn = pServer.engine.connect()
        stmt = (
            nodes_table.update()
            .where(nodes_table.c.client_id == pServer.nodes[nodeName])
            .values(last_ping=datetime.datetime.now())
        )
        conn.execute(stmt)
    else:
        raise KeyError("{0} is not a node".format(nodeName))
        # TODO: Change this to a http error code

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
        return str(streamControllerObj.isActive(pServer, None))
    else:
        raise KeyError("{0} is not a stream controller".format(streamController))
        # TODO: Change this to a http error code

@app.route("/gameState/<gameState>/<nodeName>/<status>")
def updateGameState(gameState, nodeName, status):
    heartbeatHandler(nodeName)
    if gameState in pServer.states:
        pServer.setState(gameState, int(status))
    else:
        raise KeyError("{0} is not a game state".format(gameState))
        # TODO: Change this to a http error code
    return "game state set"

class PuzzleServer:

    def __init__(self, filename):
        """
        Initialize the puzzle server with all static information and
        setup databases to hold state.
        Information concerns external nodes and game state.
        """
        with open(filename, "r") as infile:
            connections = json.load(infile)
        
        # node information
        self.nodes = {name: ID for ID, name in enumerate(connections["Nodes"])}
        self.streams = connections["Streams"]
        self.mappings = connections["Mappings"]
        
        # game state information
        self.states = {name: ID for ID, name in enumerate(connections["States"])}
        self.dependants = connections["Dependants"]
        self.dependancies = connections["Dependancies"]
        self.engine = create_engine("sqlite:///server.db", echo=True)
        metadata.bind = self.engine

        # initialize node table
        if not self.engine.dialect.has_table(self.engine, "nodes_table"):
            nodes_table.create(self.engine)
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
        
        # initialize game state table
        if not self.engine.dialect.has_table(self.engine, "game_state_table"):
            game_state_table.create(self.engine)
            i = game_state_table.insert()
            for state in self.states:
                i.execute(
                    {
                        "game_state_id": self.states[state],
                        "game_state_name": state,
                        "status": INACTIVE, 
                    }
                )
    
    def _updateState(self, stateName, newStatus):
        """
        Internal method used to update the status of a game state.
        can be passed any number but should only be passed a defined state
        """
        conn = self.engine.connect()
        updtStmt = (
            game_state_table.update()
            .where(game_state_table.c.game_state_id == self.states[stateName])
            .values(status = newStatus)
        )
        conn.execute(updtStmt)
        conn.close()

    def getState(self, stateName):
        """
        Gets the status of a given state
        """
        conn = self.engine.connect()
        selStmt = select([game_state_table]).where(game_state_table.c.game_state_id == self.states[stateName])
        results = conn.execute(selStmt)
        return results.fetchone()["status"]

    def setState(self, stateName, newStatus):
        self._updateState(stateName, newStatus)
        if newStatus == FINISHED:
            for nextState in self.dependants[stateName]:
                args = [self.getState(state) for state in self.dependancies[nextState][1:]]
                func = getattr(gameStateLogic, self.dependancies[nextState][0])
                self._updateState(nextState, ACTIVE)

    def _color(self, status):
        if status == INACTIVE:
            return INACTIVE_COLOR
        elif status == ACTIVE:
            return ACTIVE_COLOR
        elif status == FINISHED:
            return FINISHED_COLOR
        else:
            return ERROR_COLOR

    def _getGraph(self, gameStates, dependants):
        g = "digraph gameStates {"
        g += "".join([state + " [style=filled, fillcolor=" + self._color(gameStates[state]) + "];"
                                                        for state in gameStates])
        g += "".join([(state + " -> " + dState + ";")   for state in dependants
                                                        for dState in dependants[state]])
        return g + "}"

    def __str__(self):
        gameStates = {state: self.getState(state) for state in self.states}
        print(gameStates)
        g = self._getGraph(gameStates, self.dependants)
        return g

pServer = PuzzleServer("connections.json")

if __name__ == "__main__":
    app.run(threaded=True)
