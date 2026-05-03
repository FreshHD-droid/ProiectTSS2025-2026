from exceptions.transport_exceptions import InvalidCapacityError, InvalidSpeedError


class FreightTrain:

    def __init__(self, train_id, max_capacity, base_speed):
        # capacitatea trebuie sa fie strict pozitiva
        if max_capacity <= 0:
            raise InvalidCapacityError(
                "Capacitatea trenului '" + str(train_id) + "' trebuie sa fie strict pozitiva: " + str(max_capacity)
            )
        # viteza trebuie sa fie strict pozitiva
        if base_speed <= 0:
            raise InvalidSpeedError(
                "Viteza trenului '" + str(train_id) + "' trebuie sa fie strict pozitiva: " + str(base_speed)
            )
        self.train_id = train_id
        self.max_capacity = max_capacity
        self.base_speed = base_speed

    def __repr__(self):
        return "FreightTrain('" + self.train_id + "', " + str(self.max_capacity) + "t, " + str(self.base_speed) + " km/h)"
