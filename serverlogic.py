from localNode import LocalNode


class JungleCounterClass(LocalNode):
    def __init__(self):
        super().__init__("JungleCounter", 0)
        self.jungleSet = set()
    def compute(self, value):
        self.jungleSet.add(value)
        if len(self.jungleSet) >= 3:
            self.update(True)
        else:
            self.update(False)
        return self.change

JungleCounter = JungleCounterClass()
