# EscapeRoom2






## DSL Format
Three types of statements. Two connection types and node

Node(nodeName)
External device sending and recieving data.

Trigger(triggerNode, targetNode)
Forward value to the target node anytime the trigger node sends a value to the server.

Stream(triggerNode, targetNode, streamController)
stream information from trigger node to target node every x seconds while stream is active. User implements StreamController `isActive` method to control when the datat is sent.

#### Example
```
Node(PressurePlates)
Node(JungleCounter)
Node(JungleLock)
Trigger(PressurePlates, JungleCounter)
Trigger(JungleCounter, JungleLock)

Node(Dial)
Node(DialVal)
Stream(Dial, DialVal, JungleDial)
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

#### Example (from above DSL)
```json
{"Nodes": ["PressurePlates", "JungleCounter", "JungleLock", "Dial", "DialVal"], "Streams": ["JungleDial"], "Mappings": {"PressurePlates": ["JungleCounter"], "JungleCounter": ["JungleLock"], "Dial": ["DialVal"]}}
}
```
