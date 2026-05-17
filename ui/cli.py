from domain.cargo import Cargo
from domain.freight_train import FreightTrain
from domain.route import Route
from domain.transport_plan import TransportPlan
from service.transport_service import TransportService


SEPARATOR = "=" * 55
SEPARATOR_LIGHT = "-" * 55


class InteractiveCLI:

    def __init__(self):
        self.trains = {}
        self.routes = []
        self.cargo_items = []
        self.plans = {}

    # ---------- helpere pentru citire ----------

    def _read_line(self, prompt):
        # citesc un string nevid
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print("  [!] Campul nu poate fi gol.")

    def _read_float(self, prompt, default=None):
        # citesc un numar real, cu default optional
        while True:
            raw = input(prompt).strip()
            if raw == "" and default is not None:
                return default
            try:
                return float(raw)
            except ValueError:
                print("  [!] Introduceti un numar valid.")

    def _read_bool(self, prompt):
        # citesc da / nu de la utilizator
        while True:
            raw = input(prompt).strip().lower()
            if raw == "da" or raw == "d" or raw == "1":
                return True
            if raw == "nu" or raw == "n" or raw == "0":
                return False
            print("  [!] Introduceti 'da' sau 'nu'.")

    def _read_int(self, prompt, min_val, max_val):
        # citesc un numar intreg in intervalul cerut
        while True:
            raw = input(prompt).strip()
            try:
                val = int(raw)
                if val < min_val or val > max_val:
                    print("  [!] Introduceti un numar intre " + str(min_val) + " si " + str(max_val) + ".")
                    continue
                return val
            except ValueError:
                print("  [!] Introduceti un numar intreg valid.")

    # ---------- afisare plan ----------

    def _display_plan(self, plan, label="Plan"):
        # calculez greutatea totala
        total_weight = 0
        for c in plan.cargo_list:
            total_weight = total_weight + c.weight
        ratio = total_weight / plan.train.max_capacity

        print("\n" + SEPARATOR)
        print("  " + label)
        print(SEPARATOR)
        print("  Tren:         " + plan.train.train_id + " (capacitate=" + str(plan.train.max_capacity) + "t, viteza=" + str(plan.train.base_speed) + " km/h)")
        print("  Ruta:         " + plan.route.origin + " -> " + plan.route.destination + " (" + str(plan.route.distance) + " km, dificultate=" + str(plan.route.difficulty_factor) + ")")
        print("  Marfuri:")
        for cargo in plan.cargo_list:
            print("    - " + str(cargo))
        print("  Greutate:     " + str(total_weight) + "t / " + str(plan.train.max_capacity) + "t (raport=" + ("%.2f" % ratio) + ")")
        print("  Cost/km:      " + str(plan.cost_per_km))
        print("  Intarziere:   " + str(plan.delay) + "h")
        print("  ---")
        print("  Cost baza:          " + ("%.2f" % plan.base_cost()))
        print("  Suprataxare:        " + ("%.2f" % plan.weight_surcharge()))
        print("  Penalizare delay:   " + ("%.2f" % plan.delay_penalty()))
        print("  Cost total:         " + ("%.2f" % plan.total_cost()))
        print("  Durata estimata:    " + ("%.2f" % plan.estimated_duration()) + "h")
        print(SEPARATOR)

    # ---------- 1. adauga tren ----------

    def _add_train(self):
        print("\n" + SEPARATOR_LIGHT)
        print("  ADAUGA TREN")
        print(SEPARATOR_LIGHT)

        try:
            train_id = self._read_line("  ID tren: ")
            if train_id in self.trains:
                print("  [!] Trenul '" + train_id + "' exista deja.")
                return

            capacity = self._read_float("  Capacitate maxima (tone): ")
            speed = self._read_float("  Viteza de baza (km/h): ")

            train = FreightTrain(train_id, capacity, speed)
            self.trains[train_id] = train
            print("\n  [OK] Tren adaugat: " + str(train))
        except ValueError as e:
            print("\n  [!] Eroare: " + str(e))

    # ---------- 2. adauga ruta ----------

    def _add_route(self):
        print("\n" + SEPARATOR_LIGHT)
        print("  ADAUGA RUTA")
        print(SEPARATOR_LIGHT)

        try:
            origin = self._read_line("  Origine: ")
            destination = self._read_line("  Destinatie: ")
            distance = self._read_float("  Distanta (km): ")
            difficulty = self._read_float("  Factor dificultate (1.0-3.0) [Enter=1.0]: ", default=1.0)

            route = Route(origin, destination, distance, difficulty)
            self.routes.append(route)
            print("\n  [OK] Ruta adaugata: " + str(route))
        except ValueError as e:
            print("\n  [!] Eroare: " + str(e))

    # ---------- 3. adauga marfa ----------

    def _add_cargo(self):
        print("\n" + SEPARATOR_LIGHT)
        print("  ADAUGA MARFA")
        print(SEPARATOR_LIGHT)

        try:
            name = self._read_line("  Nume marfa: ")
            weight = self._read_float("  Greutate (tone): ")
            is_hazardous = self._read_bool("  Periculoasa? (da/nu): ")
            is_fragile = self._read_bool("  Fragila? (da/nu): ")

            cargo = Cargo(name, weight, is_hazardous, is_fragile)
            self.cargo_items.append(cargo)
            print("\n  [OK] Marfa adaugata: " + str(cargo))
        except ValueError as e:
            print("\n  [!] Eroare: " + str(e))

    # ---------- 4. creeaza plan ----------

    def _create_plan(self):
        print("\n" + SEPARATOR_LIGHT)
        print("  CREEAZA PLAN DE TRANSPORT")
        print(SEPARATOR_LIGHT)

        if not self.trains:
            print("  [!] Nu exista trenuri. Adaugati un tren mai intai (optiunea 1).")
            return
        if not self.routes:
            print("  [!] Nu exista rute. Adaugati o ruta mai intai (optiunea 2).")
            return
        if not self.cargo_items:
            print("  [!] Nu exista marfuri. Adaugati o marfa mai intai (optiunea 3).")
            return

        try:
            plan_name = self._read_line("  Nume plan: ")
            if plan_name in self.plans:
                print("  [!] Planul '" + plan_name + "' exista deja.")
                return

            # selectare tren
            print("\n  Trenuri disponibile:")
            train_ids = list(self.trains.keys())
            for i in range(len(train_ids)):
                print("    " + str(i + 1) + ". " + str(self.trains[train_ids[i]]))
            idx = self._read_int("  Selectati trenul (numar): ", 1, len(train_ids))
            train = self.trains[train_ids[idx - 1]]

            # selectare ruta
            print("\n  Rute disponibile:")
            for i in range(len(self.routes)):
                print("    " + str(i + 1) + ". " + str(self.routes[i]))
            idx = self._read_int("  Selectati ruta (numar): ", 1, len(self.routes))
            route = self.routes[idx - 1]

            # selectare marfuri
            print("\n  Marfuri disponibile:")
            for i in range(len(self.cargo_items)):
                print("    " + str(i + 1) + ". " + str(self.cargo_items[i]))
            print("  Introduceti numerele marfurilor separate prin virgula")
            raw = self._read_line("  (ex: 1,3 sau 'toate'): ")

            if raw.lower() == "toate":
                selected_cargo = list(self.cargo_items)
            else:
                # parsez numerele introduse de utilizator
                indices = []
                parts = raw.split(",")
                for x in parts:
                    indices.append(int(x.strip()))
                selected_cargo = []
                for i in indices:
                    if i >= 1 and i <= len(self.cargo_items):
                        selected_cargo.append(self.cargo_items[i - 1])
                    else:
                        print("  [!] Index invalid: " + str(i))
                        return

            if not selected_cargo:
                print("  [!] Nu ati selectat nicio marfa.")
                return

            cost_per_km = self._read_float("\n  Cost per km: ")
            delay = self._read_float("  Intarziere ore [Enter=0]: ", default=0.0)

            plan = TransportPlan(train, route, selected_cargo, cost_per_km, delay)
            self.plans[plan_name] = plan

            print("\n  [OK] Plan creat cu succes!")
            self._display_plan(plan, "Plan: " + plan_name)
        except ValueError as e:
            print("\n  [!] Eroare: " + str(e))

    # ---------- 5. listeaza entitati ----------

    def _list_all(self):
        print("\n" + SEPARATOR)
        print("  ENTITATI IN SISTEM")
        print(SEPARATOR)

        print("\n  Trenuri (" + str(len(self.trains)) + "):")
        if self.trains:
            for tid in self.trains:
                print("    - " + str(self.trains[tid]))
        else:
            print("    (niciun tren)")

        print("\n  Rute (" + str(len(self.routes)) + "):")
        if self.routes:
            for i in range(len(self.routes)):
                print("    " + str(i + 1) + ". " + str(self.routes[i]))
        else:
            print("    (nicio ruta)")

        print("\n  Marfuri (" + str(len(self.cargo_items)) + "):")
        if self.cargo_items:
            for i in range(len(self.cargo_items)):
                print("    " + str(i + 1) + ". " + str(self.cargo_items[i]))
        else:
            print("    (nicio marfa)")

        print("\n  Planuri (" + str(len(self.plans)) + "):")
        if self.plans:
            for name in self.plans:
                p = self.plans[name]
                cost = p.total_cost()
                duration = p.estimated_duration()
                print("    - [" + name + "] " + p.train.train_id + ", " + p.route.origin + "->" + p.route.destination + ", cost=" + ("%.2f" % cost) + ", durata=" + ("%.2f" % duration) + "h")
        else:
            print("    (niciun plan)")

        print(SEPARATOR)

    # ---------- 6. detalii plan ----------

    def _show_plan_details(self):
        if not self.plans:
            print("\n  [!] Nu exista planuri create.")
            return

        print("\n" + SEPARATOR_LIGHT)
        print("  DETALII PLAN")
        print(SEPARATOR_LIGHT)

        plan_names = list(self.plans.keys())
        print("  Planuri disponibile:")
        for i in range(len(plan_names)):
            print("    " + str(i + 1) + ". " + plan_names[i])

        idx = self._read_int("  Selectati planul (numar): ", 1, len(plan_names))
        name = plan_names[idx - 1]
        self._display_plan(self.plans[name], "Plan: " + name)

    # ---------- 7. compara planuri ----------

    def _compare_plans(self):
        if len(self.plans) < 2:
            print("\n  [!] Aveti " + str(len(self.plans)) + " plan(uri). Sunt necesare cel putin 2 pentru comparare.")
            return

        print("\n" + SEPARATOR_LIGHT)
        print("  COMPARA PLANURI")
        print(SEPARATOR_LIGHT)

        plan_names = list(self.plans.keys())
        print("  Planuri disponibile:")
        for i in range(len(plan_names)):
            print("    " + str(i + 1) + ". " + plan_names[i])

        idx_a = self._read_int("  Selectati Plan A (numar): ", 1, len(plan_names))
        idx_b = self._read_int("  Selectati Plan B (numar): ", 1, len(plan_names))

        if idx_a == idx_b:
            print("  [!] Selectati doua planuri diferite.")
            return

        name_a = plan_names[idx_a - 1]
        name_b = plan_names[idx_b - 1]
        plan_a = self.plans[name_a]
        plan_b = self.plans[name_b]

        self._display_plan(plan_a, "Plan A: " + name_a)
        self._display_plan(plan_b, "Plan B: " + name_b)

        service = TransportService()
        result = service.compare_plans(plan_a, plan_b)

        print("\n" + SEPARATOR)
        print("  REZULTAT COMPARATIE")
        print(SEPARATOR)
        print("  Cost:   Plan A = " + ("%.2f" % result["cost_a"]) + "  |  Plan B = " + ("%.2f" % result["cost_b"]))
        print("  Durata: Plan A = " + ("%.2f" % result["duration_a"]) + "h |  Plan B = " + ("%.2f" % result["duration_b"]) + "h")
        print("  ---")
        print("  Recomandare: " + result["recommendation"])
        print("  Motiv:       " + result["reason"])
        print(SEPARATOR)

    # ---------- 8. sterge entitate ----------

    def _delete_entity(self):
        print("\n" + SEPARATOR_LIGHT)
        print("  STERGE ENTITATE")
        print(SEPARATOR_LIGHT)
        print("  1. Sterge tren")
        print("  2. Sterge ruta")
        print("  3. Sterge marfa")
        print("  4. Sterge plan")
        print("  0. Inapoi")

        choice = input("\n  Alegeti: ").strip()

        if choice == "1":
            self._delete_train()
        elif choice == "2":
            self._delete_route()
        elif choice == "3":
            self._delete_cargo()
        elif choice == "4":
            self._delete_plan()
        elif choice == "0":
            return
        else:
            print("  [!] Optiune invalida.")

    def _delete_train(self):
        if not self.trains:
            print("  [!] Nu exista trenuri.")
            return

        train_ids = list(self.trains.keys())
        for i in range(len(train_ids)):
            print("    " + str(i + 1) + ". " + str(self.trains[train_ids[i]]))

        idx = self._read_int("  Trenul de sters (numar): ", 1, len(train_ids))
        tid = train_ids[idx - 1]
        removed = self.trains.pop(tid)
        print("  [OK] Trenul '" + tid + "' a fost sters.")

        # caut planurile care folosesc trenul sters
        affected = []
        for name in self.plans:
            if self.plans[name].train is removed:
                affected.append(name)
        # le sterg
        for name in affected:
            del self.plans[name]
        # afisez ce s-a sters
        if affected:
            names_str = ""
            for i in range(len(affected)):
                if i > 0:
                    names_str = names_str + ", "
                names_str = names_str + "'" + affected[i] + "'"
            print("  [OK] Planuri sterse (foloseau trenul): " + names_str)

    def _delete_route(self):
        if not self.routes:
            print("  [!] Nu exista rute.")
            return

        for i in range(len(self.routes)):
            print("    " + str(i + 1) + ". " + str(self.routes[i]))

        idx = self._read_int("  Ruta de stearsa (numar): ", 1, len(self.routes))
        removed = self.routes.pop(idx - 1)
        print("  [OK] Ruta '" + removed.origin + " -> " + removed.destination + "' a fost stearsa.")

        # caut planurile care folosesc ruta stearsa
        affected = []
        for name in self.plans:
            if self.plans[name].route is removed:
                affected.append(name)
        # le sterg
        for name in affected:
            del self.plans[name]
        # afisez ce s-a sters
        if affected:
            names_str = ""
            for i in range(len(affected)):
                if i > 0:
                    names_str = names_str + ", "
                names_str = names_str + "'" + affected[i] + "'"
            print("  [OK] Planuri sterse (foloseau ruta): " + names_str)

    def _delete_cargo(self):
        if not self.cargo_items:
            print("  [!] Nu exista marfuri.")
            return

        for i in range(len(self.cargo_items)):
            print("    " + str(i + 1) + ". " + str(self.cargo_items[i]))

        idx = self._read_int("  Marfa de stearsa (numar): ", 1, len(self.cargo_items))
        removed = self.cargo_items.pop(idx - 1)
        print("  [OK] Marfa '" + removed.name + "' a fost stearsa.")

        # caut planurile care contineau marfa stearsa
        affected = []
        for name in self.plans:
            plan = self.plans[name]
            for cargo in plan.cargo_list:
                if cargo is removed:
                    affected.append(name)
                    break
        # le sterg
        for name in affected:
            del self.plans[name]
        # afisez ce s-a sters
        if affected:
            names_str = ""
            for i in range(len(affected)):
                if i > 0:
                    names_str = names_str + ", "
                names_str = names_str + "'" + affected[i] + "'"
            print("  [OK] Planuri sterse (contineau marfa): " + names_str)

    def _delete_plan(self):
        if not self.plans:
            print("  [!] Nu exista planuri.")
            return

        plan_names = list(self.plans.keys())
        for i in range(len(plan_names)):
            print("    " + str(i + 1) + ". " + plan_names[i])

        idx = self._read_int("  Planul de sters (numar): ", 1, len(plan_names))
        name = plan_names[idx - 1]
        del self.plans[name]
        print("  [OK] Planul '" + name + "' a fost sters.")

    # ---------- meniu principal ----------

    def _show_menu(self):
        print("\n--- MENIU PRINCIPAL ---")
        print("  1. Adauga tren")
        print("  2. Adauga ruta")
        print("  3. Adauga marfa")
        print("  4. Creeaza plan de transport")
        print("  5. Listeaza entitati")
        print("  6. Detalii plan")
        print("  7. Compara doua planuri")
        print("  8. Sterge entitate")
        print("  0. Iesire")

    def run(self):
        # bucla principala
        print("\n" + SEPARATOR)
        print("  Transport Feroviar de Marfa")
        print("  Sistem de planificare")
        print(SEPARATOR)

        while True:
            self._show_menu()
            choice = input("\nAlegeti optiunea: ").strip()

            if choice == "1":
                self._add_train()
            elif choice == "2":
                self._add_route()
            elif choice == "3":
                self._add_cargo()
            elif choice == "4":
                self._create_plan()
            elif choice == "5":
                self._list_all()
            elif choice == "6":
                self._show_plan_details()
            elif choice == "7":
                self._compare_plans()
            elif choice == "8":
                self._delete_entity()
            elif choice == "0":
                print("\nLa revedere!")
                break
            else:
                print("\n  [!] Optiune invalida. Incercati din nou.")


def main():
    try:
        cli = InteractiveCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\nLa revedere!")
    return 0
