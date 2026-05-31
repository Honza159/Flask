# inventar.py - sprava batohu hrace
# MAX_SLOTS = maximalni pocet predmetu v batohu najednou

MAX_SLOTS = 8


class Predmet:
    # jeden predmet ve hre - nazev, typ, bonusy atd.

    def __init__(self, predmet_id: str, data: dict):
        self.id           = predmet_id
        self.nazev        = data.get('nazev', predmet_id)
        self.typ          = data.get('typ', 'ostatni')
        self.popis        = data.get('popis', '')
        self.bonus_utok   = data.get('bonus_utok', 0)
        self.bonus_obrana = data.get('bonus_obrana', 0)
        self.obnova_zivotu = data.get('obnova_zivotu', 0)

    # pomocne metody pro kontrolu typu predmetu
    def je_lektvar(self)  -> bool: return self.typ == 'lektvar'
    def je_zbran(self)    -> bool: return self.typ == 'zbran'
    def je_brneni(self)   -> bool: return self.typ == 'brneni'
    def je_klicovy(self)  -> bool: return self.typ == 'klicovy'

    def __repr__(self):
        return f"<Predmet {self.id}: {self.nazev} ({self.typ})>"


class Inventar:

    @staticmethod
    def pouzij_lektvar(predmet_id: str, aktualni_hp: int, max_hp: int,
                       definice_predmetu: dict) -> tuple:
        # pouziti lektvaru - vrati (nove_hp, zprava_pro_hrace)
        predmet = definice_predmetu.get(predmet_id)
        if not predmet or predmet.get('typ') != 'lektvar':
            return aktualni_hp, "Tento předmět nejde použít jako lektvar."

        obnova          = predmet.get('obnova_zivotu', 0)
        nove_hp         = min(max_hp, aktualni_hp + obnova)
        skutecna_obnova = nove_hp - aktualni_hp  # realne obnovene HP (ne vic nez max)

        return nove_hp, f"Použil jsi {predmet['nazev']} a obnovil {skutecna_obnova} HP."

    @staticmethod
    def je_plny(inventar: list) -> bool:
        # True = batoh plny, nejde pridat dalsi predmet
        return len(inventar) >= MAX_SLOTS
