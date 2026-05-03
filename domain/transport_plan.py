from exceptions.transport_exceptions import (
    NegativeCostError,
    NegativeDelayError,
    CapacityExceededError,
    EmptyCargoListError,
)


class TransportPlan:

    def __init__(self, train, route, cargo_list, cost_per_km, delay=0.0):
        # validari
        if not cargo_list:
            raise EmptyCargoListError("Lista de marfuri nu poate fi goala")
        if cost_per_km < 0:
            raise NegativeCostError("Costul per km nu poate fi negativ: " + str(cost_per_km))
        if delay < 0:
            raise NegativeDelayError("Intarzierea nu poate fi negativa: " + str(delay))

        # calculez greutatea totala
        total_weight = 0
        for c in cargo_list:
            total_weight = total_weight + c.weight

        # verific daca incape in tren
        if total_weight > train.max_capacity:
            raise CapacityExceededError(
                "Greutatea totala (" + str(total_weight) + "t) depaseste capacitatea trenului (" + str(train.max_capacity) + "t)"
            )

        self.train = train
        self.route = route
        self.cargo_list = cargo_list
        self.cost_per_km = cost_per_km
        self.delay = delay

    def base_cost(self):
        # cost de baza = distanta * cost per km
        return self.route.distance * self.cost_per_km

    def weight_surcharge(self):
        # calculez greutatea totala
        total_weight = 0
        for c in self.cargo_list:
            total_weight = total_weight + c.weight

        # raportul greutate / capacitate
        ratio = total_weight / self.train.max_capacity
        cost = self.base_cost()

        # praguri pentru suprataxa
        if ratio <= 0.5:
            return cost * 0.25
        elif ratio <= 0.8:
            return cost * 0.10
        else:
            return 0.0

    def delay_penalty(self):
        # penalizare in functie de orele de intarziere
        if self.delay <= 0:
            return 0.0
        elif self.delay <= 2:
            return 50.0
        elif self.delay <= 6:
            return 50.0 + (self.delay - 2) * 30.0
        else:
            return 50.0 + 120.0 + (self.delay - 6) * 50.0

    def estimated_duration(self):
        # durata = distanta / viteza * factor dificultate
        base_duration = (self.route.distance / self.train.base_speed) * self.route.difficulty_factor

        # caut daca exista marfa periculoasa sau fragila
        has_hazardous = False
        has_fragile = False
        for c in self.cargo_list:
            if c.is_hazardous:
                has_hazardous = True
            if c.is_fragile:
                has_fragile = True

        # aplic ajustarile
        if has_hazardous and has_fragile:
            base_duration = base_duration * 1.20
        elif has_hazardous or has_fragile:
            base_duration = base_duration * 1.10

        # adaug intarzierea la final
        return base_duration + self.delay

    def total_cost(self):
        # cost total = cost de baza + suprataxa greutate + penalizare delay
        return self.base_cost() + self.weight_surcharge() + self.delay_penalty()

    def __repr__(self):
        return "TransportPlan(tren=" + self.train.train_id + ", ruta=" + self.route.origin + "->" + self.route.destination + ", marfuri=" + str(len(self.cargo_list)) + ", cost_total=" + ("%.2f" % self.total_cost()) + ")"
