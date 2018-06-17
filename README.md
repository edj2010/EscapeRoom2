# EscapeRoom2






## DSL Format
Four types of statements. Two connection types and two node types
RemoteNode(nodeName)
device not on the server computer

LocalNode(nodeName)
local class/variable that stores some information (for more complicated processing between external nodes)

Trigger(triggerNode, targetNode)
notify target node anytime trigger node sends an update to the server

Stream(triggerNode, targetNode, streamControllerName)
stream information from trigger nod)
e to target node while stream is active (controlled by stream controller)

#### Example
```
RemoteNode(PressurePlates)  
LocalNode(JungleCounter)  
RemoteNode(JungleLock)  
Trigger(PressurePlates, JungleCounter)  
Trigger(JungleCounter, JungleLock)  

RemoteNode(Dial)  
LocalNode(DialVal)  
Stream(Dial, DialVal, JungleDial)  
```
## JSON format

DSL information converted to JSON for parsing by server
JSON formatted as follows:
{"LocalNodes": [list, of, local, node, names],
 "RemoteNodes": [list, of, remote, node, names],
 "Streams": [list, of, stream, controller, names],
 "Mappings": {inputNodeName: [output, Node, Names]}}

"LocalNodes" is a list of all local nodes in the system
"RemoteNodes" is a list of all remote nodes in the system
"Streams" is a list of all stream controller names
"Mappings" is a list of all trigger and stream mapping information (if information is available for input, which outputs do I update

#### Example (from above DSL)
```json
{"LocalNodes": ["JungleCounter", "DialVal"],
 "RemoteNodes": ["PressurePlates", "JungleLock", "Dial"],
 "Streams": ["JungleDial"],
 "Mappings": {"PressurePlates": ["JungleCounter"],
              "JungleCounter": ["JungleLock"],
              "Dial": ["DialVal"]}
}
```
