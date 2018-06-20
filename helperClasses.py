class StreamController:
    def __init__(self, name):
        self.name = name

    def isActive(self, localVals, gameState):
        raise NotImplementedError("This is an abstract function. Please implement")
