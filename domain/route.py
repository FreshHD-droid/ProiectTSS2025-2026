from exceptions.transport_exceptions import NegativeDistanceError, InvalidDifficultyFactorError


class Route:

    def __init__(self, origin, destination, distance, difficulty_factor=1.0):
        # distanta nu poate fi negativa
        if distance < 0:
            raise NegativeDistanceError(
                "Distanta rutei nu poate fi negativa: " + str(distance)
            )
        # factorul trebuie sa fie intre 1.0 si 3.0
        if difficulty_factor < 1.0 or difficulty_factor > 3.0:
            raise InvalidDifficultyFactorError(
                "Factorul de dificultate trebuie sa fie intre 1.0 si 3.0: " + str(difficulty_factor)
            )
        self.origin = origin
        self.destination = destination
        self.distance = distance
        self.difficulty_factor = difficulty_factor

    def __repr__(self):
        return "Route('" + self.origin + "' -> '" + self.destination + "', " + str(self.distance) + " km, dificultate=" + str(self.difficulty_factor) + ")"
