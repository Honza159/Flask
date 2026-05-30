class Hrdina:
    """Třída reprezentující hrdinu – hráčovu postavu."""

    BASE_UTOK = 10
    BASE_OBRANA = 5

    def __init__(self, jmeno: str, hp: int = 100, max_hp: int = 100):
        self.jmeno = jmeno
        self.hp = hp
        self.max_hp = max_hp
        self.base_utok = self.BASE_UTOK
        self.base_obrana = self.BASE_OBRANA

    def spocti_statistiky(self, inventar: list, definice_predmetu: dict) -> tuple:
        """Spočítá útok a obranu hrdiny včetně bonusů z vybavení v inventáři."""
        utok = self.base_utok
        obrana = self.base_obrana

        for predmet_id in inventar:
            predmet = definice_predmetu.get(predmet_id, {})
            utok += predmet.get("bonus_utok", 0)
            obrana += predmet.get("bonus_obrana", 0)

        return utok, obrana

    def je_nazivu(self) -> bool:
        """Vrátí True pokud je hrdina stále naživu."""
        return self.hp > 0

    def procento_hp(self) -> int:
        """Vrátí aktuální životy jako procento z maxima (pro HP bar)."""
        if self.max_hp == 0:
            return 0
        return max(0, min(100, int((self.hp / self.max_hp) * 100)))
