import json
import os


def nacti_svet() -> dict:
    #Načte data světa ze souboru svet.json
    cesta = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'svet.json')
    with open(cesta, 'r', encoding='utf-8') as f:
        return json.load(f)


def ziskej_mapu(aktualni_id: str) -> str:
    #Vrátí ASCII mapu ostrova s označením aktuální polohy hráče. Každá lokace je označena zkratkou. hráčova pozice nahrazena [ *TY* ]
    mapa = (
        "  [SLP.UL]--[Z.KRILO]    [PRACOVNA]\n"
        "                 |           |\n"
        "             [FONTANA]---[KANCELAR]+\n"
        "                 |           |\n"
        "  [V.HALA]--[NADVORI]   [GARAZE]\n"
        "                 |           |\n"
        "  [  CELA]--[CHODBA ]---[ZAHRADA]--[PRISTAV]"
    )

    znacky = {
        'slepa_ulicka_kam_10': '[SLP.UL]',
        'chodba_kam_9':        '[Z.KRILO]',
        'trezor_kam_11':       '[PRACOVNA]',
        'fontana_kam_7':       '[FONTANA]',
        'kancelar_kam_8':      '[KANCELAR]',
        'vstupni_hala_kam_4':  '[V.HALA]',
        'nadvori_kam_2':       '[NADVORI]',
        'garaze_kam_5':        '[GARAZE]',
        'cela_start':          '[  CELA]',
        'chodba_kam_1':        '[CHODBA ]',
        'zahrada_kam_3':       '[ZAHRADA]',
        'pristav_kam_6':       '[PRISTAV]',
    }

    znacka = znacky.get(aktualni_id)
    if znacka:
        mapa = mapa.replace(znacka, '[ *TY* ]', 1)

    return mapa
