class Hrdina:
    def __init__(self, jmeno, hp=100, max_hp=100):
        self.jmeno = jmeno
        self.hp = hp
        self.max_hp = max_hp
        self.base_utok = 10  # Základní útok bez zbraně
        self.base_obrana = 5  # Základní obrana bez vesty

    def spocti_statistiky(self, inventar, definice_predmetu):
        #vezme veci z inventáře a přičte hodnoty bonusů
        utok = self.base_utok
        obrana = self.base_obrana

        for predmet_id in inventar:
            predmet = definice_predmetu.get(predmet_id, {})
            utok += predmet.get("bonus_utok", 0)
            obrana += predmet.get("bonus_obrana", 0)

        return utok, obrana