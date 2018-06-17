'''
RemoteNode(PressurePlates)
LocalNode(JungleCounter)
RemoteNode(JungleLock)
Trigger(PressurePlates, JungleCounter)
Trigger(JungleCounter, JungleLock)

RemoteNode(Dial)
LocalNode(DialVal)
Stream(Dial, DialVal, JungleDial)

JSONIFY

{"LocalNodes": ["JungleCounter", "DialVal"],
 "RemoteNodes": ["PressurePlates", "JungleLock", "Dial"],
 "Streams": ["JungleDial"]
 "Triggers": {"PressurePlates": ["JungleCounter"],
              "JungleCounter": ["JungleLock"],
              "Dial": ["DialVal"]}
}


'''

def main():
    DSLParse("connections.pzl")

def DSLParse(filename):
    
