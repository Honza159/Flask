import random


def vypocti_poskozeni(utok: int, obrana: int) -> int:
    """
    Vypočítá poškození útočníka vůči cíli.
    Výsledek je ovlivněn náhodou v rozmezí -2 až +3.
    Poškození nikdy neklesne pod 1 (vždy alespoň symbolický úder).
    """
    poskozeni = (utok - obrana) + random.randint(-2, 3)
    return max(1, poskozeni)
