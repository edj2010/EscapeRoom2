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
        raise NotImplementedError("This is an abstract function. Please implement")

    def get(self):
        return self.value
