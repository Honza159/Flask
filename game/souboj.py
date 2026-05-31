import random
#utok - obrana + nahodna odchylka
#minimum je vzdy 1, aby utok nikdy neselhal uplne

def vypocti_poskozeni(utok: int, obrana: int) -> int:
    poskozeni = (utok - obrana) + random.randint(-2, 3)
    return max(1, poskozeni)
