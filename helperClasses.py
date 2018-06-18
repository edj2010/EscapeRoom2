class LocalNode:
    def __init__(self, name, initVal):
        self.name = name
        self.value = initVal
        self.change = True

    def update(self, value):
        if value != self.value:
            self.change = True
            self.value = value

    def compute(self, value):
        """Given some input value, should return (self.change, self.value)"""
        raise NotImplementedError("This is an abstract function. Please implement")

    def get(self):
        return self.value


class StreamController:
    def __init__(self, name):
        self.name = name

    def isActive(self, localVals, gameState):
        raise NotImplementedError("This is an abstract function. Please implement")
