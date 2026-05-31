class Hrdina:

    # zakladni hodnoty
    BASE_UTOK   = 10
    BASE_OBRANA = 5

    def __init__(self, jmeno: str, hp: int = 100, max_hp: int = 100):
        self.jmeno      = jmeno
        self.hp         = hp
        self.max_hp     = max_hp
        self.base_utok   = self.BASE_UTOK
        self.base_obrana = self.BASE_OBRANA

    def spocti_statistiky(self, inventar: list, definice_predmetu: dict) -> tuple:
        # projde inventar a pricte bonusy ze zbrani, brneni atd.
        utok   = self.base_utok
        obrana = self.base_obrana

        for pid in inventar:
            predmet = definice_predmetu.get(pid, {})
            utok   += predmet.get('bonus_utok',   0)
            obrana += predmet.get('bonus_obrana', 0)

        return utok, obrana

    def je_nazivu(self) -> bool:
        # vrati True dokud ma hrdina aspon 1 HP
        return self.hp > 0

    def procento_hp(self) -> int:
        # pro HP bar v sablone. vraci 0-100
        if self.max_hp == 0:
            return 0
        return max(0, min(100, int(self.hp / self.max_hp * 100)))
