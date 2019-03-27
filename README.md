# EscapeRoom2


## Running the Server
Make sure that you have the virtual environment activated by running `pipenv shell` at the root of the repo, and that all dependencies are up to date with `pipenv install`. To run the server in debug mode, run `python server/server.py` to run the server in production mode, `cd ./server` and then `gunicorn -w 4 -b 127.0.0.1:5000 wsgi`

## Working on the Front-end
Before working on the front-end, make sure to have the server running, and then `cd ./static` and run `npm run watch`. This will automatically rebuild the compiled js files whenever you save changes. Also run `npm install` from the `static` folder to make sure that you have all the required dependencies installed.


## DSL Format
Five types of statements. Three connection types, node, and state

`Node(nodeName)`
External device sending and recieving data.

`Trigger(triggerNode, targetNode)`
Defines a flow of information, that forwards values input by the triggerNode to the targetNode.

`Stream(triggerNode, targetNode, streamController)`
Streams are triggers that also create an 'isActive' API endpoint, which calls a user provided function. This should be used to turn on high frequency data flows (ie every .5 seconds) only when they are needed.

`State(stateName)`
Game state node, used for tracking progress in the room. (states Begin and End are declared implicitely)

`Dependency(outState, funcName, inputState1, inputState2, ...)`
defines a dependancy, where out state goes from inactive to active if funcName returns true given the statuses of inputState1, ... inputStateN. Checked anytime one of the input states is finished. funcName must be defined in gameStateLogic.py (unless it is AND or OR, which are already defined). funcName can be ommitted if only one inputState (then it's just if a then b)

#### Example
```
Node(PressurePlates)
Node(JungleCounter)
Node(JungleLock)
Trigger(PressurePlates, JungleCounter)
Trigger(JungleCounter, JungleLock)

Node(Dial)
Node(DialOut)
Stream(Dial, DialOut, JungleDial)

State(JungleUnlocked)
Dependancy(JungleUnlocked, Begin)
Dependancy(End, JungleUnlocked)
```
## JSON format

DSL information converted to JSON for parsing by server
JSON formatted as follows:
```
{"Nodes": [list, of, node, names],
 "Streams": [list, of, stream, controller, names],
 "Mappings": {inputNodeName: [output, node, names], ...},
 "States": [list, of, state, names],
 "Dependants": {inputState: [output, state, names], ...},
 "Dependancies": {outputState: [funcName, input, state, names]}}
```
"Nodes" is a list of all nodes in the room
"Streams" is a list of all stream controller names
"Mappings" is a list of all trigger and stream mapping information (if information is available for input, which outputs do I update
"States" is a list of all state names
"Dependants" is a list of all input states, and the output nodes that depend on them
"Dependancies" is a list of all output states, funcName/input states required to activate it

##### Example (from above DSL)
```json
{"Nodes": ["PressurePlates", "JungleCounter", "JungleLock", "Dial", "DialOut"],
 "Streams": ["JungleDial"],
 "Mappings": {"PressurePlates": ["JungleCounter"],
              "JungleCounter": ["JungleLock"],
              "Dial": ["DialOut"]
             },
 "States": ["Begin", "JungleUnlocked", "End"],
 "Dependants": {"Begin": ["JungleUnlocked"],
                "JungleUnlocked": ["End"]
               },
 "Dependancies": {"JungleUnlocked": ["AND", "Begin"],
                  "End": ["AND", "JungleUnlocked"]
                 }
}
```

## Stream Controllers
In order to limit the load on the server, Triggers that have a very high load, and especially those that send values every `x` seconds, rather than in response to input should consider whether they can use a stream controller to avoid sending information through the server when it is not needed. To do this, after creating a Stream in the DSL (eg. `Stream(Dial, DialOut, JungleDial)`), you need to create an object that subclasses `StreamController` in `serverlogic.py`.

#### Example
```python
class JungleDialClass(StreamController):
    def __init__(self):
        super().__init__("JungleDial")

    def isActive(self, gameState):
        return gameState.isActive("JungleDial")
```

Note that the server will not actually deactivate the flow of information from input node to output node, but nodes are expected to periodically query the StreamController API to decide whether or not to send queries to the input and output APIs.
