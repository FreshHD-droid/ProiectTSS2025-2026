# exceptii custom pentru aplicatie

class NegativeWeightError(ValueError):
    pass


class NegativeDistanceError(ValueError):
    pass


class NegativeCostError(ValueError):
    pass


class NegativeDelayError(ValueError):
    pass


class InvalidCapacityError(ValueError):
    pass


class InvalidSpeedError(ValueError):
    pass


class CapacityExceededError(ValueError):
    pass


class EmptyCargoListError(ValueError):
    pass


class InvalidDifficultyFactorError(ValueError):
    pass
