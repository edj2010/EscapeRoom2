from helperClasses import LocalNode
from helperClasses import StreamController


class JungleCounterClass(LocalNode):
    def __init__(self):
        super().__init__("JungleCounter", 0)
        self.jungleSet = set()

    def compute(self, value):
        self.jungleSet.add(value)
        self.update(len(self.jungleSet))
        return self.change, self.value


JungleCounter = JungleCounterClass()


class JungleDialClass(StreamController):
    def __init__(self):
        super().__init__("JungleDial")

    def isActive(self, localVals, gameState):
        if "JungleCounter" in localVals and 1 < localVals["JungleCounter"] < 3:
            return True
        return False


JungleDial = JungleDialClass()
