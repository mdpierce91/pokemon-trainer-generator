
from consts import F_MINUS_TIER, S_PLUS_TIER


class TierRange():
    low: int
    high: int

    def __init__(self, low:int=F_MINUS_TIER, high:int=S_PLUS_TIER):
        self.low = low
        self.high = high
        pass