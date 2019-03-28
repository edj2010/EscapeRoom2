from flask import *

IP = "127.0.0.1"

application = Flask(__name__)

@application.route("/setIP/<ip>")
def setIP(ip):
    global IP
    IP=ip
    return "IP set"

@application.route("/getIP")
def getIP():
    return IP

if __name__ == "__main__":
    application.run(threaded=True, host = '0.0.0.0')
