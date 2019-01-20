# Node Test Bed
# Evan Johnson
# Jan 15 2019

# Desired functionality includes:
#  sending specific requests from specific nodes
#  setting up a node to constantly ping server heartbeat
#  having list of nodes be loadable from a file

import requests
import sys
from time import sleep

NODES = {}
BASE_URL = "localhost:5000"

def sendHeartbeat(nodeName):
    url = f"http://{BASE_URL}/heartbeat/{nodeName}"
    r = requests.post(url)

def main():
    PERIOD = 3
    # Get base url for requests
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
    
    # Run loop for reading in instructions
    while True:
        Input = input(">").split()
        if (Input[0] == "help"):
            print("\n".join([ "help - list all commands",
                    "addNode <nodeName> <active> - add node to list of nodes. If active then set node to ping server every cycle (default false)",
                    "addNodesFromFile <fileName> - adds all nodes listed in file, file must be a series of lines of form <nodeName> <active>",
                    "setActive <nodeName> <active> - sets the activity of nodeName to active(true) or inactive(false) depending on what <active> is set to",
                    "run - continuously pings server from active nodes until user enters Ctrl-C",
                    "saveNodes <fileName> - saves existing nodes in appropriate format to specified file",
                    "ping <nodeName> - sends heartbeat ping to server to update specified node's status",
                    "setLoop <loopPeriod> - sets loop period in seconds for run ping frequency"]) + "\n")
        
        elif (Input[0] == "addNode"):
            active = False
            if len(Input) >= 3:
                active = (Input[2].lower() == 'true')
            NODES[Input[1]] = active

        elif (Input[0] == "addNodesFromFile"):
            try:
                with open(Input[1], 'r+') as f:
                    for line in f.readlines():
                        if line != "\n":
                            name, active = line.strip().split()
                            active = bool(active)
                            NODES[name] = active
            except:
                print("Problem reading file")

        elif (Input[0] == "setActive"):
            active = (Input[2].lower() == 'true')
            NODES[Input[1]] = active

        elif (Input[0] == "run"):
            print("Nodes: " + ", ".join(NODES))
            try:
                i = 0
                while True:
                    i += 1
                    print(f"Ping Loop {i}.")
                    for node in NODES:
                        if NODES[node]:
                            sendHeartbeat(node)
                    sleep(PERIOD)
            except Exception as e:
                print("running terminated: " + str(e))
            except:
                print("running terminated")

        elif (Input[0] == "saveNodes"):
            with open(Input[1], "w+") as f:
                strings = [node + " " + str(NODES[node]) + "\n" for node in NODES]
                for s in strings:
                    f.write(s)
        

        elif (Input[0] == "ping"):
            sendHeartbeat(Input[1])

        elif (Input[0] == "setLoop"):
            PERIOD = float(Input[1])

if __name__ == "__main__":
    main()
