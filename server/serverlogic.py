from helperClasses import StreamController


class JungleDialClass(StreamController):
    def __init__(self):
        super().__init__("JungleDial")

    def isActive(self, localVals, gameState):
        if "JungleCounter" in localVals and 1 < localVals["JungleCounter"] < 3:
            return True
        return False


JungleDial = JungleDialClass()
