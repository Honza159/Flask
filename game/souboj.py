import random


def vypocti_poskozeni(utok, obrana):
    poskozeni = (utok - obrana) + random.randint(-2, 3)

    if poskozeni < 0:
        poskozeni = 0

    return poskozeni