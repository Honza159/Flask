import json
import os


def nacti_svet():
    cesta = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'svet.json')
    with open(cesta, 'r', encoding='utf-8') as f:
        return json.load(f)

def ziskej_mapu(aktualni_id):
    mapa = """
    [ CAM 10]--[ CAM 9 ]           [ CAM 11]
                   |                   |
               [ CAM 7 ]---[ CAM 8 ]---+
                   |           |
    [ CAM 4 ]--[ CAM 2 ]   [ CAM 5 ]
                   |           |
    [  CELA ]--[ CAM 1 ]---[ CAM 3 ]--[ CAM 6 ]
    """

    znacky = {
        'slepa_ulicka_kam_10': '[ CAM 10]',
        'chodba_kam_9': '[ CAM 9 ]',
        'trezor_kam_11': '[ CAM 11]',
        'fontana_kam_7': '[ CAM 7 ]',
        'kancelar_kam_8': '[ CAM 8 ]',
        'vstupni_hala_kam_4': '[ CAM 4 ]',
        'nadvori_kam_2': '[ CAM 2 ]',
        'garaze_kam_5': '[ CAM 5 ]',
        'cela_start': '[  CELA ]',
        'chodba_kam_1': '[ CAM 1 ]',
        'zahrada_kam_3': '[ CAM 3 ]',
        'pristav_kam_6': '[ CAM 6 ]'
    }

    if aktualni_id in znacky:
        mapa = mapa.replace(znacky[aktualni_id], '[ *TY* ]')

    return mapa