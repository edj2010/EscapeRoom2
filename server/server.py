import json
from sqlalchemy import create_engine, select
from collections import defaultdict
import serverlogic
import gameStateLogic
from gameStateLogic import INACTIVE, ACTIVE, FINISHED
from flask import Flask
from flask import render_template, jsonify
from models import game_state_table, nodes_table, metadata
import datetime
import simpleaudio as sa
import wave

app = Flask(__name__, static_folder = "../static/dist", template_folder = "../static")

# Game State constants
INACTIVE_COLOR = "grey73"
ACTIVE_COLOR = "gold1"
FINISHED_COLOR = "darkolivegreen3"
ERROR_COLOR = "indianred3"
FUNC_COLOR = "skyblue"

AUDIO_PATH = "../Sound/"


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
        print(self.nodes)
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
        """
        Sets the status of a given state. If status is FINISHED, updates the statuses
        of dependant nodes based on their respective activation functions.
        """
        self._updateState(stateName, newStatus)
        if newStatus == FINISHED:
            for nextState in self.dependants[stateName]:
                args = [self.getState(state) for state in self.dependancies[nextState][1:]]
                func = getattr(gameStateLogic, self.dependancies[nextState][0])
                if(func(args)):
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
        """
        Constructs a graphviz format graph of the game state and returns it
        """
        funcNameCount = defaultdict(int)

        def getFuncName(name):
            n = name + str(funcNameCount[name])
            funcNameCount[name]+=1
            return n

        uniqueFuncNames = {name: getFuncName(self.dependancies[name][0]) for name in self.dependancies}
        
        g = "digraph gameStates {"
        g += "".join([state + " [style=filled, fillcolor=" + self._color(gameStates[state]) + "];"
                                                        for state in gameStates])
        g += "".join([func + " [style=filled, fillcolor=" + FUNC_COLOR + "];" for func in uniqueFuncNames.values()])
        g += "".join([uniqueFuncNames[state] + " -> " + state + ";"
                                                        for state in self.dependancies])
        g += "".join([state + " -> " + uniqueFuncNames[dState] + ";"
                                                        for state in self.dependants
                                                        for dState in dependants[state]])
        return g + "}"

    def __str__(self):
        """
        toString method for puzzle server
        Currently just prints graph of game states in dict and graph form
        """
        gameStates = {state: self.getState(state) for state in self.states}
        g = str(gameStates) + "\n"
        g+= self._getGraph(gameStates, self.dependants)
        return g

pServer = PuzzleServer("connections.json")



## GUI
@app.route("/")
def gameroom():
    """
    Generic landing screen
    """
    return render_template("index.html")

@app.route("/controlroom")
def controlRoom():
    """
    Control Room landing screen
    """
    return render_template("controlroom.html")


## Server API
@app.route("/getdata")
def getData():
    """
    Get server state
    """
    return jsonify({'hint_text': "Blank Text",
                    'hint_exists': True,
                    'time': 7200,
                    'paused': True,
                    'gamestate': "ongoing"})


## ESP API
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


@app.route("/streamStatus/<nodeName>/<streamController>")
def streamStatus(nodeName, streamController):
    """
    Checks whether a given stream is active or not
    Requires nodeName to update heartbeat
    """
    heartbeatHandler(nodeName)
    if streamController in pServer.streams:
        streamControllerObj = getattr(serverlogic, streamController)
        return str(streamControllerObj.isActive(pServer, None))
    else:
        raise KeyError("{0} is not a stream controller".format(streamController))
        # TODO: Change this to a http error code

@app.route("/gameState/<nodeName>/<gameState>/<status>")
def updateGameState(nodeName, gameState, status):
    """
    API for ESP updating gamestate
    Requires nodeName to update heartbeat
    """
    heartbeatHandler(nodeName)
    if gameState in pServer.states:
        pServer.setState(gameState, int(status))
        print(pServer)
    else:
        raise KeyError("{0} is not a game state".format(gameState))
        # TODO: Change this to a http error code
    return "game state set"

@app.route("/playAudio/<nodeName>/<audioFile>")
def playAudio(nodeName, audioFile):
    """
    Interface used by the nodes to play audio from the server
    Audio selected by file name and stored on the server computer
    """
    heartbeatHandler(nodeName)
    # TODO: ensure that multiple web workers running will not interfere
    wav_obj = sa.WaveObject.from_wave_file(AUDIO_PATH + audioFile)
    play_obj = wav_obj.play()
    play_obj.wait_done()
    return "Audio Completed"

if __name__ == "__main__":
    app.run(threaded=True)
