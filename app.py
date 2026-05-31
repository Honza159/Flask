from flask import Flask, render_template, request, session, redirect, url_for
from game.mapa import nacti_svet, ziskej_mapu
from game.hrdina import Hrdina
from game.inventar import Inventar, MAX_SLOTS
from game.souboj import vypocti_poskozeni

app = Flask(__name__)
app.secret_key = 'tajny_klic_uteku_z_ostrova_2024'


# -----------------------------------------------------------------------
# POMOCNA FUNKCE - zkrati opakujici se kod
# vrati hrdinu + jeho utok a obranu ze session
# -----------------------------------------------------------------------
def get_hrdina_stats():
    svet_data = nacti_svet()
    hrdina = Hrdina(session['jmeno_hrdiny'], session['hrdina_hp'], session['hrdina_max_hp'])
    utok, obrana = hrdina.spocti_statistiky(session['inventar'], svet_data['predmety'])
    return svet_data, utok, obrana


# -----------------------------------------------------------------------
# UVODNI STRANKA - zadani jmena, inicializace nove hry
# -----------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        jmeno = request.form.get('jmeno', '').strip()
        if not jmeno:
            return render_template('index.html')

        svet_data = nacti_svet()
        session.clear()

        # zakladni hodnoty hrdiny
        session['jmeno_hrdiny'] = jmeno
        session['aktualni_lokace'] = 'cela_start'
        session['inventar'] = []
        session['hrdina_hp'] = 100
        session['hrdina_max_hp'] = 100

        # predmety v lokacich - kopie ze JSON aby se daly sebrat/vyhodit
        session['mapa_predmetu'] = {
            loc_id: list(loc['predmety_zde'])
            for loc_id, loc in svet_data['lokace'].items()
        }

        # nepratele - kopie ze JSON, sledujeme aktualni HP
        session['nepratele'] = {
            nid: dict(ndata)
            for nid, ndata in svet_data['nepratele'].items()
        }

        return redirect(url_for('hra'))
    return render_template('index.html')


# -----------------------------------------------------------------------
# HLAVNI STRANKA HRY - zobrazeni lokace, mapy, predmetu
# -----------------------------------------------------------------------
@app.route('/hra')
def hra():
    if 'jmeno_hrdiny' not in session:
        return redirect(url_for('index'))

    svet_data, utok, obrana = get_hrdina_stats()
    id_lokace = session['aktualni_lokace']

    return render_template('hra.html',
        jmeno        = session['jmeno_hrdiny'],
        lokace       = svet_data['lokace'][id_lokace],
        id_lokace    = id_lokace,
        mapa         = ziskej_mapu(id_lokace),
        predmety_zde = session['mapa_predmetu'][id_lokace],
        definice_predmetu = svet_data['predmety'],
        hp           = session['hrdina_hp'],
        max_hp       = session['hrdina_max_hp'],
        utok         = utok,
        obrana       = obrana,
        zprava       = session.pop('herni_zprava', None),
        ma_klice     = 'klice_od_clunu' in session['inventar'],
        pocet_slotu  = len(session['inventar']),
        max_slotu    = MAX_SLOTS
    )


# -----------------------------------------------------------------------
# POHYB - hrac klikne na smer (doleva/doprava/dopredu/dozadu)
# -----------------------------------------------------------------------
@app.route('/jdi/<smer>')
def jdi(smer):
    if 'aktualni_lokace' not in session:
        return redirect(url_for('index'))

    svet_data = nacti_svet()
    lokace = svet_data['lokace'][session['aktualni_lokace']]
    vychody = lokace.get('vychody', {})

    if smer not in vychody:
        return redirect(url_for('hra'))

    cil = vychody[smer]

    # trezor je zamceny bez flash disku
    if cil == 'trezor_kam_11' and 'zasifrovany_disk' not in session['inventar']:
        session['herni_zprava'] = (
            "Dveře jsou elektronicky zamčené. Potřebuješ přístupový kód "
            "(flash disk z místnosti v západním křídle)."
        )
        return redirect(url_for('hra'))

    session['aktualni_lokace'] = cil

    # je v cilove lokaci zijici nepritel? → spustit souboj
    nepritel_id = svet_data['lokace'][cil].get('nepritel')
    if nepritel_id and session['nepratele'][nepritel_id]['hp'] > 0:
        session['zprava_souboj'] = f"Cestu ti zablokoval {session['nepratele'][nepritel_id]['nazev']}!"
        return redirect(url_for('souboj'))

    return redirect(url_for('hra'))


# -----------------------------------------------------------------------
# ODPLOUT - win condition, hrac ma klice a je na pristavnim mole
# -----------------------------------------------------------------------
@app.route('/odplout')
def odplout():
    if 'klice_od_clunu' not in session.get('inventar', []):
        session['herni_zprava'] = "Člun tu je, ale chybí ti klíče. Najdi je nejdřív!"
        return redirect(url_for('hra'))
    return redirect(url_for('konec', vysledek='vyhra'))


# -----------------------------------------------------------------------
# INVENTAR - zobrazeni vsech predmetu u hrace
# -----------------------------------------------------------------------
@app.route('/inventar')
def inventar_stranka():
    if 'jmeno_hrdiny' not in session:
        return redirect(url_for('index'))

    svet_data, utok, obrana = get_hrdina_stats()

    return render_template('inventar.html',
        inventar          = session['inventar'],
        definice_predmetu = svet_data['predmety'],
        hp                = session['hrdina_hp'],
        max_hp            = session['hrdina_max_hp'],
        utok              = utok,
        obrana            = obrana,
        zprava            = session.pop('inventar_zprava', None),
        pocet_slotu       = len(session['inventar']),
        max_slotu         = MAX_SLOTS
    )


# sebrat predmet ze zeme
@app.route('/vezmi/<id_predmetu>')
def vezmi(id_predmetu):
    if 'aktualni_lokace' not in session:
        return redirect(url_for('index'))

    if len(session['inventar']) >= MAX_SLOTS:
        session['herni_zprava'] = f"Batoh je plný! (max {MAX_SLOTS} předmětů) Nejdřív něco vyhoď."
        return redirect(url_for('hra'))

    lokace_predmety = session['mapa_predmetu'][session['aktualni_lokace']]
    if id_predmetu in lokace_predmety:
        lokace_predmety.remove(id_predmetu)
        session['inventar'].append(id_predmetu)
        session['herni_zprava'] = "Sebral jsi předmět."
        session.modified = True

    return redirect(url_for('hra'))


# pouzit lektvar z inventare (mimo souboj)
@app.route('/pouzi/<id_predmetu>')
def pouzi(id_predmetu):
    svet_data = nacti_svet()
    predmet = svet_data['predmety'].get(id_predmetu, {})

    if predmet.get('typ') == 'lektvar':
        nove_hp, zprava = Inventar.pouzij_lektvar(
            id_predmetu, session['hrdina_hp'], session['hrdina_max_hp'], svet_data['predmety']
        )
        session['hrdina_hp'] = nove_hp
        session['inventar'].remove(id_predmetu)
        session['inventar_zprava'] = zprava
        session.modified = True

    return redirect(url_for('inventar_stranka'))


# vyhodit predmet na zem aktualni lokace
@app.route('/vyhod/<id_predmetu>')
def vyhod(id_predmetu):
    if id_predmetu in session['inventar']:
        session['inventar'].remove(id_predmetu)
        session['mapa_predmetu'][session['aktualni_lokace']].append(id_predmetu)
        session['inventar_zprava'] = "Předmět jsi vyhodil na zem."
        session.modified = True
    return redirect(url_for('inventar_stranka'))


# -----------------------------------------------------------------------
# SOUBOJ - zobrazeni soubojove obrazovky
# -----------------------------------------------------------------------
@app.route('/souboj')
def souboj():
    if 'aktualni_lokace' not in session:
        return redirect(url_for('index'))

    svet_data, utok, obrana = get_hrdina_stats()
    id_lokace    = session['aktualni_lokace']
    nepritel_id  = svet_data['lokace'][id_lokace]['nepritel']
    nepritel     = session['nepratele'][nepritel_id]

    # seznam lektvaru ktere ma hrac u sebe (muzou se pouzit v souboji)
    lektvary = [
        pid for pid in session['inventar']
        if svet_data['predmety'].get(pid, {}).get('typ') == 'lektvar'
    ]

    return render_template('souboj.html',
        hp       = session['hrdina_hp'],
        max_hp   = session['hrdina_max_hp'],
        utok     = utok,
        obrana   = obrana,
        nepritel = nepritel,
        zprava   = session.pop('zprava_souboj', 'Boj začíná!'),
        lektvary = lektvary,
        definice_predmetu = svet_data['predmety']
    )


# pouzit lektvar primo behem souboje - nepritel pak zautoCI (prominuty tah)
@app.route('/pouzi_v_souboji/<id_predmetu>')
def pouzi_v_souboji(id_predmetu):
    if 'aktualni_lokace' not in session:
        return redirect(url_for('index'))

    svet_data    = nacti_svet()
    id_lokace    = session['aktualni_lokace']
    nepritel_id  = svet_data['lokace'][id_lokace]['nepritel']
    nepritel     = session['nepratele'][nepritel_id]
    predmet      = svet_data['predmety'].get(id_predmetu, {})

    if id_predmetu in session['inventar'] and predmet.get('typ') == 'lektvar':
        # hrac se lecí - ale ztraci tah, nepritel zautoCI
        nove_hp, zprava_lektvaru = Inventar.pouzij_lektvar(
            id_predmetu, session['hrdina_hp'], session['hrdina_max_hp'], svet_data['predmety']
        )
        session['hrdina_hp'] = nove_hp
        session['inventar'].remove(id_predmetu)

        # utok nepritele za prominuty tah
        hrdina = Hrdina(session['jmeno_hrdiny'], session['hrdina_hp'], session['hrdina_max_hp'])
        _, obrana = hrdina.spocti_statistiky(session['inventar'], svet_data['predmety'])
        dmg = vypocti_poskozeni(nepritel['utok'], obrana)
        session['hrdina_hp'] -= dmg
        session.modified = True

        if session['hrdina_hp'] <= 0:
            return redirect(url_for('konec', vysledek='prohra'))

        session['zprava_souboj'] = f"{zprava_lektvaru} Nepřítel využil příležitosti a udeřil za {dmg} DMG!"

    return redirect(url_for('souboj'))


# -----------------------------------------------------------------------
# AKCE V SOUBOJI - utok nebo utek
# -----------------------------------------------------------------------
@app.route('/akce_souboj/<akce>')
def akce_souboj(akce):
    if 'aktualni_lokace' not in session:
        return redirect(url_for('index'))

    svet_data   = nacti_svet()
    id_lokace   = session['aktualni_lokace']
    nepritel_id = svet_data['lokace'][id_lokace]['nepritel']
    nepritel    = session['nepratele'][nepritel_id]

    # --- UTEK - hrac se vraci do cely ---
    if akce == 'utek':
        session['aktualni_lokace'] = 'cela_start'
        session['herni_zprava'] = "Utekl jsi v panice zpět do cely."
        return redirect(url_for('hra'))

    # --- UTOK HRACE na nepritele ---
    if akce == 'utok':
        hrdina = Hrdina(session['jmeno_hrdiny'], session['hrdina_hp'], session['hrdina_max_hp'])
        utok_h, obrana_h = hrdina.spocti_statistiky(session['inventar'], svet_data['predmety'])

        # utok uzivatele - snizi HP nepritele
        dmg_na_nepritele = vypocti_poskozeni(utok_h, nepritel['obrana'])
        nepritel['hp'] -= dmg_na_nepritele
        session.modified = True

        # nepritel mrtvy → loot + navrat do hry
        if nepritel['hp'] <= 0:
            drop_id     = svet_data['nepratele'][nepritel_id].get('drop')
            zprava_loot = ""
            if drop_id and len(session['inventar']) < MAX_SLOTS:
                session['inventar'].append(drop_id)
                zprava_loot = f" Získal jsi: {svet_data['predmety'][drop_id]['nazev']}!"

            if nepritel_id == 'magnat':
                session['herni_zprava'] = f"Porazil jsi Magnáta!{zprava_loot} Nyní jdi na přístav a odpluj!"
            else:
                session['herni_zprava'] = f"Nepřítel poražen!{zprava_loot} Můžeš pokračovat."

            session.modified = True
            return redirect(url_for('hra'))

        # nepritel zije → utoci zpet na hrace
        dmg_na_hrace = vypocti_poskozeni(nepritel['utok'], obrana_h)
        session['hrdina_hp'] -= dmg_na_hrace

        if session['hrdina_hp'] <= 0:
            return redirect(url_for('konec', vysledek='prohra'))

        session['zprava_souboj'] = (
            f"Udělil jsi {dmg_na_nepritele} DMG. "
            f"Nepřítel ti vrátil úder za {dmg_na_hrace} DMG."
        )
        session.modified = True

    return redirect(url_for('souboj'))


# -----------------------------------------------------------------------
# KONEC HRY - vyhra nebo prohra, vymaze session
# -----------------------------------------------------------------------
@app.route('/konec/<vysledek>')
def konec(vysledek):
    session.clear()
    return render_template('konec.html', vysledek=vysledek)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
