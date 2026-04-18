class TransportService:

    def compare_plans(self, plan_a, plan_b):
        # iau costurile si duratele
        cost_a = plan_a.total_cost()
        cost_b = plan_b.total_cost()
        duration_a = plan_a.estimated_duration()
        duration_b = plan_b.estimated_duration()

        # decid ce plan e mai bun
        if cost_a < cost_b and duration_a <= duration_b:
            recommendation = "Plan A"
            reason = "cost mai mic si durata mai mica sau egala"
        elif cost_b < cost_a and duration_b <= duration_a:
            recommendation = "Plan B"
            reason = "cost mai mic si durata mai mica sau egala"
        elif cost_a < cost_b:
            recommendation = "Plan A"
            reason = "cost mai mic, dar durata mai mare"
        elif cost_b < cost_a:
            recommendation = "Plan B"
            reason = "cost mai mic, dar durata mai mare"
        elif duration_a < duration_b:
            recommendation = "Plan A"
            reason = "cost egal, durata mai mica"
        elif duration_b < duration_a:
            recommendation = "Plan B"
            reason = "cost egal, durata mai mica"
        else:
            recommendation = "Echivalent"
            reason = "cost si durata identice"

        # construiesc dictionarul cu rezultatul
        result = {}
        result["cost_a"] = cost_a
        result["cost_b"] = cost_b
        result["duration_a"] = duration_a
        result["duration_b"] = duration_b
        result["recommendation"] = recommendation
        result["reason"] = reason
        return result
