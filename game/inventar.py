class Inventar:
    @staticmethod
    def pouzij_lektvar(predmet_id, aktualni_hp, max_hp, definice_predmetu):
        predmet = definice_predmetu.get(predmet_id)
        if not predmet or predmet.get("typ") != "lektvar":
            return aktualni_hp, "Tento předmět nelze použít jako lektvar."

        obnova = predmet.get("obnova_zivotu", 0)
        nove_hp = min(max_hp, aktualni_hp + obnova)
        zprava = f"Použil jsi {predmet['nazev']} a obnovil jsi {nove_hp - aktualni_hp} HP."

        return nove_hp, zprava