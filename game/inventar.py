MAX_SLOTS = 8  # Maximální počet předmětů v batohu


class Predmet:
    """Třída reprezentující jeden předmět ve hře."""

    def __init__(self, predmet_id: str, data: dict):
        self.id = predmet_id
        self.nazev = data.get("nazev", predmet_id)
        self.typ = data.get("typ", "ostatni")
        self.popis = data.get("popis", "")
        self.bonus_utok = data.get("bonus_utok", 0)
        self.bonus_obrana = data.get("bonus_obrana", 0)
        self.obnova_zivotu = data.get("obnova_zivotu", 0)

    def je_lektvar(self) -> bool:
        return self.typ == "lektvar"

    def je_zbran(self) -> bool:
        return self.typ == "zbran"

    def je_brneni(self) -> bool:
        return self.typ == "brneni"

    def je_klicovy(self) -> bool:
        return self.typ == "klicovy"

    def __repr__(self) -> str:
        return f"<Predmet {self.id}: {self.nazev} ({self.typ})>"


class Inventar:
    """Třída pro správu inventáře hrdiny."""

    @staticmethod
    def pouzij_lektvar(predmet_id: str, aktualni_hp: int, max_hp: int,
                       definice_predmetu: dict) -> tuple:
        """
        Použije lektvar z inventáře a vrátí nové HP a zprávu.
        Vrátí (nove_hp, zprava_str).
        """
        predmet = definice_predmetu.get(predmet_id)
        if not predmet or predmet.get("typ") != "lektvar":
            return aktualni_hp, "Tento předmět nelze použít jako lektvar."

        obnova = predmet.get("obnova_zivotu", 0)
        nove_hp = min(max_hp, aktualni_hp + obnova)
        skutecna_obnova = nove_hp - aktualni_hp
        zprava = f"Použil jsi {predmet['nazev']} a obnovil jsi {skutecna_obnova} HP."

        return nove_hp, zprava

    @staticmethod
    def je_plny(inventar: list) -> bool:
        """Vrátí True pokud je batoh plný."""
        return len(inventar) >= MAX_SLOTS
