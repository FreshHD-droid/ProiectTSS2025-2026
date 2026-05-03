from exceptions.transport_exceptions import NegativeDelayError, EmptyCargoListError


class RiskEvaluator:

    def evaluate_shipment_risk(self, cargo_list, train, route, delay_hours):
        # validari
        if delay_hours < 0:
            raise NegativeDelayError("Intarzierea nu poate fi negativa: " + str(delay_hours))
        if not cargo_list:
            raise EmptyCargoListError("Lista de marfuri nu poate fi goala")

        # calculez greutatea totala si greutatea marfurilor periculoase
        total_weight = 0
        hazardous_weight = 0
        for c in cargo_list:
            total_weight = total_weight + c.weight
            if c.is_hazardous:
                hazardous_weight = hazardous_weight + c.weight

        # raportul greutate / capacitate
        ratio = total_weight / train.max_capacity

        # marfa periculoasa + tren aproape plin => risc maxim
        if hazardous_weight > 0 and ratio > 0.7:
            return "HIGH"

        # ruta dificila + intarziere mare => risc maxim
        if route.difficulty_factor >= 2.0 and delay_hours > 4:
            risk = "HIGH"
        else:
            if ratio > 0.5:
                risk = "MEDIUM"
            else:
                risk = "LOW"

        return risk
