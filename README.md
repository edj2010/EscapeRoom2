# EscapeRoom2






## DSL Format
Three types of statements. Two connection types and node

Node(nodeName)
External device sending and recieving data.

Trigger(triggerNode, targetNode)
Defines a flow of information, that forwards values input by the trigger node to the target node.

Stream(triggerNode, targetNode, streamController)
Streams are triggers that also create an 'isActive' API endpoint, which calls a user provided function. This should be used to turn on high frequency data flows (ie every .5 seconds) only when they are needed.

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
```
## JSON format

DSL information converted to JSON for parsing by server
JSON formatted as follows:
{"Nodes": [list, of, node, names],
 "Streams": [list, of, stream, controller, names],
 "Mappings": {inputNodeName: [output, node, names]}}

"Nodes" is a list of all nodes in the system
"Streams" is a list of all stream controller names
"Mappings" is a list of all trigger and stream mapping information (if information is available for input, which outputs do I update

##### Example (from above DSL)
```json
{"Nodes": ["PressurePlates", "JungleCounter", "JungleLock", "Dial", "DialOut"],
 "Streams": ["JungleDial"],
 "Mappings": {"PressurePlates": ["JungleCounter"],
              "JungleCounter": ["JungleLock"],
              "Dial": ["DialOut"]
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
