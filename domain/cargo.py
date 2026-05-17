from exceptions.transport_exceptions import NegativeWeightError


class Cargo:

    def __init__(self, name, weight, is_hazardous=False, is_fragile=False):
        # validare greutate
        if weight < 0:
            raise NegativeWeightError(
                "Greutatea marfii '" + str(name) + "' nu poate fi negativa: " + str(weight)
            )
        self.name = name
        self.weight = weight
        self.is_hazardous = is_hazardous
        self.is_fragile = is_fragile

    def __repr__(self):
        # construiesc textul cu flag-urile
        if self.is_hazardous and self.is_fragile:
            flags = " [periculos, fragil]"
        elif self.is_hazardous:
            flags = " [periculos]"
        elif self.is_fragile:
            flags = " [fragil]"
        else:
            flags = ""
        return "Cargo('" + self.name + "', " + str(self.weight) + "t" + flags + ")"
