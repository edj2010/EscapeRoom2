import json
from sqlalchemy import create_engine, select
from collections import defaultdict
import serverlogic
import gameStateLogic
from gameStateLogic import INACTIVE, ACTIVE, FINISHED
from flask import Flask
from flask import render_template, jsonify, request
from models import gameroom_table, game_state_table, nodes_table, metadata
import datetime
import simpleaudio as sa
import wave
import time

app = Flask(__name__, static_folder = "../static/dist", template_folder = "../static")

# Game State constants
BEGIN_STATE = 'Begin'
END_STATE = 'End'

INACTIVE_COLOR = "grey73"
ACTIVE_COLOR = "gold1"
FINISHED_COLOR = "darkolivegreen3"
ERROR_COLOR = "indianred3"
FUNC_COLOR = "skyblue"

AUDIO_PATH = "../Sound/"
GAME_LEN = 3600

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

        # initialize gameroom table
        if not self.engine.dialect.has_table(self.engine, "gameroom_table"):
            gameroom_table.create(self.engine)
            i = gameroom_table.insert()
            i.execute(
                {
                    'gameroom_id': 1,
                    'hint_text': "",
                    'hint_exists': False,
                    'hint_timer': 0,
                    'start_time': 0,
                    'end_time': 0,
                    'paused': True,
                    'gamestate': "unstarted",
                }
            )

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

        if stateName == END_STATE and (newStatus == ACTIVE or newStatus == FINISHED):
            self.wonGame()

    def startGame(self):
        """
        Starts the game, initializes the start timer
        """
        conn = self.engine.connect()
        updtStmt = (
            gameroom_table.update()
            .where(gameroom_table.c.gameroom_id == 1)
            .values({'start_time': int(time.time()),
                     'gamestate': "ongoing",
                     'paused': False
                    })
            )
        conn.execute(updtStmt)
        conn.close()        
        self._updateState(BEGIN_STATE, ACTIVE)

    def resetGame(self):
        """
        Resets the game, clears start timer
        """
        conn = self.engine.connect()
        updtStmt = (
            gameroom_table.update()
            .where(gameroom_table.c.gameroom_id == 1)
            .values({'start_time': 0,
                     'end_time': 0,
                     'gamestate': "unstarted",
                     'paused': True
                    })
            )
        conn.execute(updtStmt)
        conn.close()
        for state in self.states:
            self._updateState(state, INACTIVE)

    def wonGame(self):
        """
        Ends the game, bringing the user to the winning end screen
        """
        conn = self.engine.connect()
        updtStmt = (
            gameroom_table.update()
            .where(gameroom_table.c.gameroom_id == 1)
            .values({'end_time': int(time.time()),
                     'gamestate': "completed",
                    }) 
            )
        conn.execute(updtStmt)
        conn.close()

    def lostGame(self):
        """
        Ends the game, bringing the user to the losing end screen
        """
        conn = self.engine.connect()
        updtStmt = (
            gameroom_table.update()
            .where(gameroom_table.c.gameroom_id == 1)
            .values({'gamestate': "out_of_time"})
                )
        conn.execute(updtStmt)
        conn.close()

    def getRoomInfo(self):
        """
        Gets info relevant to display in game room
        """
        conn = self.engine.connect()
        selStmt = select([gameroom_table]).where(gameroom_table.c.gameroom_id == 1)
        results = dict(conn.execute(selStmt).fetchone())
        results["time"] = GAME_LEN - (int(time.time()) - results["start_time"])
        print(results)
        if results["time"] < 0 and results["gamestate"] == "ongoing":
            results["gamestate"] = "out_of_time"
            self.lostGame()
        return results

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
                if self.getState(nextState) == INACTIVE:
                    args = [self.getState(state) for state in self.dependancies[nextState][1:]]
                    func = getattr(gameStateLogic, self.dependancies[nextState][0])
                    if(func(args)):
                        self._updateState(nextState, ACTIVE)
        elif newStatus == INACTIVE:
            for nextState in self.dependants[stateName]:
                if self.getState(nextState) == ACTIVE:
                    args = [self.getState(state) for state in self.dependancies[nextState][1:]]
                    func = getattr(gameStateLogic, self.dependancies[nextState][0])
                    if(not func(args)):
                        self.setState(nextState, INACTIVE)

    def getNodesByStatus(self, status):
        conn = self.engine.connect()
        selStmt = select([game_state_table]).where(game_state_table.c.status == status)
        results = conn.execute(selStmt)
        return list(results.fetchall())

    def getHeartbeats(self):
        conn = self.engine.connect()
        selStmt = select([nodes_table])
        results = conn.execute(selStmt)
        return list(results)

    def setHint(self, new_hint_text,  new_hint_timer, new_hint_exists):
        conn = self.engine.connect()
        updtStmt = (
            gameroom_table.update()
            .where(gameroom_table.c.gameroom_id == 1)
            .values({
                "hint_text": new_hint_text,
                "hint_exists": new_hint_exists,
                "hint_timer": new_hint_timer
            })
        )
        conn.execute(updtStmt)
        conn.close()


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
        return self._getGraph(gameStates, self.dependants)

pServer = PuzzleServer("connections.json")



## GUI
@app.route("/")
def gameroom():
    """
    Game Room landing screen
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
    roominfo = pServer.getRoomInfo()
    del roominfo["start_time"]
    return jsonify(roominfo)

@app.route("/graph")
def getGraph():
    return str(pServer)

@app.route("/nodeStates")
def getActiveNodes():
    inactive_node_names = [{"id": x[0], "name": x[1]} for x in pServer.getNodesByStatus(INACTIVE)]
    active_node_names = [{"id": x[0], "name": x[1]} for x in pServer.getNodesByStatus(ACTIVE)]
    finished_node_names = [{"id": x[0], "name": x[1]} for x in pServer.getNodesByStatus(FINISHED)]
    return jsonify({'inactive': inactive_node_names,
                    'active': active_node_names,
                    'finished': finished_node_names})

@app.route("/heartbeats")
def getHeartbeats():
    results = pServer.getHeartbeats()
    print(results)
    return jsonify([{"name": row[1], "time": row[2].timestamp()} for row in results])

@app.route("/start")
def start():
    """
    Starts the game
    """
    pServer.startGame()
    return "Game Started"

@app.route("/reset")
def reset():
    """
    Resets the game
    """
    pServer.resetGame()
    return "Game Reset"

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

@app.route("/gameStateESP/<nodeName>/<gameState>/<status>")
def updateGameStateESP(nodeName, gameState, status):
    """
    API for ESP updating gamestate
    Requires nodeName to update heartbeat
    """
    heartbeatHandler(nodeName)
    return updateGameState(gameState, status)

@app.route("/gameState/<gameState>/<status>")
def updateGameState(gameState, status):
    """
    API for updating gamestate from web
    """
    if gameState in pServer.states:
        pServer.setState(gameState, int(status))
        print(pServer)
    else:
        raise KeyError("{0} is not a game state".format(gameState))
        # TODO: Change this to a http error code
    return "game state set"

@app.route("/gameState/<gameState>/toggle")
def toggleGameState(gameState):
    """
    Sets state to completed if the state was INACTIVE or ACTIVE
    Sets state to INACTIVE if the state was FINISHED and then
    checks if it should be updated
    """
    if gameState in pServer.states:
        if pServer.getState(gameState) != FINISHED:
            pServer.setState(gameState, FINISHED)
        else:
            pServer.setState(gameState, INACTIVE)
            args = [pServer.getState(state) for state in pServer.dependancies[gameState][1:]]
            func = getattr(gameStateLogic, pServer.dependancies[gameState][0])
            if func(args):
                pServer.setState(gameState, ACTIVE)
    return "game state toggled"


@app.route("/playAudio/<nodeName>/<audioFile>")
def playAudioESP(nodeName, audioFile):
    heartbeatHandler(nodeName)
    return playAudio(audioFile)

@app.route("/playAudio/<audioFile>")
def playAudio(audioFile):
    """
    Interface used by the nodes to play audio from the server
    Audio selected by file name and stored on the server computer
    """
    # TODO: ensure that multiple web workers running will not interfere
    wav_obj = sa.WaveObject.from_wave_file(AUDIO_PATH + audioFile)
    play_obj = wav_obj.play()
    play_obj.wait_done()
    return "Audio Completed"


@app.route("/setHint", methods=['POST'])
def setHint():
    pServer.setHint(request.form["hint_message"], request.form["hint_timer"], True)
    return "Hint Recieved", 204


if __name__ == "__main__":
    app.run(threaded=True)

