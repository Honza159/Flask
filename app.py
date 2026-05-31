from flask import Flask, render_template, request, session, redirect, url_for
from game.mapa import nacti_svet, ziskej_mapu
from game.hrdina import Hrdina
from game.inventar import Inventar, MAX_SLOTS
from game.souboj import vypocti_poskozeni

app = Flask(__name__)
app.secret_key = 'tajny_klic_uteku_z_ostrova_2024'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        jmeno = request.form.get('jmeno', '').strip()
        if jmeno:
            session.clear()
            session['jmeno_hrdiny'] = jmeno
            session['aktualni_lokace'] = 'cela_start'
            session['inventar'] = []
            session['hrdina_hp'] = 100
            session['hrdina_max_hp'] = 100

            svet_data = nacti_svet()

            # Načtení předmětů v lokacích ze JSON
            mapa_predmetu = {}
            for id_lokace, lokace_info in svet_data['lokace'].items():
                mapa_predmetu[id_lokace] = list(lokace_info['predmety_zde'])
            session['mapa_predmetu'] = mapa_predmetu

            # Načtení nepřátel ze JSON (uchovávají se aktuální HP)
            nepratele = {}
            for id_nepritele, stats in svet_data['nepratele'].items():
                nepratele[id_nepritele] = dict(stats)
            session['nepratele'] = nepratele

            return redirect(url_for('hra'))
    return render_template('index.html')


@app.route('/hra')
def hra():
    if 'jmeno_hrdiny' not in session:
        return redirect(url_for('index'))

    svet_data = nacti_svet()
    id_lokace = session['aktualni_lokace']
    lokace_data = svet_data['lokace'].get(id_lokace)

    textova_mapa = ziskej_mapu(id_lokace)
    predmety_v_lokaci = session['mapa_predmetu'][id_lokace]
    definice_predmetu = svet_data['predmety']

    hrdina = Hrdina(session['jmeno_hrdiny'], session['hrdina_hp'], session['hrdina_max_hp'])
    utok, obrana = hrdina.spocti_statistiky(session['inventar'], definice_predmetu)

    zprava = session.pop('herni_zprava', None)
    ma_klice = 'klice_od_clunu' in session['inventar']
    pocet_slotu = len(session['inventar'])

    return render_template(
        'hra.html',
        jmeno=session['jmeno_hrdiny'],
        lokace=lokace_data,
        id_lokace=id_lokace,
        mapa=textova_mapa,
        predmety_zde=predmety_v_lokaci,
        definice_predmetu=definice_predmetu,
        hp=session['hrdina_hp'],
        max_hp=session['hrdina_max_hp'],
        utok=utok,
        obrana=obrana,
        zprava=zprava,
        ma_klice=ma_klice,
        pocet_slotu=pocet_slotu,
        max_slotu=MAX_SLOTS
    )


@app.route('/jdi/<smer>')
def jdi(smer):
    if 'aktualni_lokace' not in session:
        return redirect(url_for('index'))

    svet_data = nacti_svet()
    aktualni_id = session['aktualni_lokace']
    lokace_data = svet_data['lokace'].get(aktualni_id)

    if lokace_data and smer in lokace_data['vychody']:
        nova_lokace_id = lokace_data['vychody'][smer]

        # Klíčový předmět – brána do trezoru
        if nova_lokace_id == 'trezor_kam_11' and 'zasifrovany_disk' not in session['inventar']:
            session['herni_zprava'] = (
                "Dveře jsou elektronicky zamčené. Potřebuješ přístupový kód "
                "(flash disk z místnosti v západním křídle)."
            )
            return redirect(url_for('hra'))

        session['aktualni_lokace'] = nova_lokace_id

        # Pokud je v nové lokaci živý nepřítel, začíná boj
        nova_lokace_data = svet_data['lokace'].get(nova_lokace_id)
        id_nepritele = nova_lokace_data.get('nepritel')
        if id_nepritele and session['nepratele'][id_nepritele]['hp'] > 0:
            session['zprava_souboj'] = (
                f"Cestu ti zablokoval {session['nepratele'][id_nepritele]['nazev']}!"
            )
            return redirect(url_for('souboj'))

    return redirect(url_for('hra'))


@app.route('/odplout')
def odplout():
    """Win condition – odplutí na člunu s klíči."""
    if 'klice_od_clunu' not in session.get('inventar', []):
        session['herni_zprava'] = "Člun tu je, ale chybí ti klíče. Najdi je nejdřív!"
        return redirect(url_for('hra'))
    return redirect(url_for('konec', vysledek='vyhra'))


# ── INVENTÁŘ ──────────────────────────────────────────────────────────────────

@app.route('/vezmi/<id_predmetu>')
def vezmi(id_predmetu):
    if 'aktualni_lokace' not in session:
        return redirect(url_for('index'))

    aktualni_id = session['aktualni_lokace']

    if len(session['inventar']) >= MAX_SLOTS:
        session['herni_zprava'] = f"Batoh je plný! (max {MAX_SLOTS} předmětů) Nejdřív něco vyhoď."
        return redirect(url_for('hra'))

    if id_predmetu in session['mapa_predmetu'][aktualni_id]:
        session['mapa_predmetu'][aktualni_id].remove(id_predmetu)
        session['inventar'].append(id_predmetu)
        session['herni_zprava'] = "Sebral jsi předmět."
        session.modified = True

    return redirect(url_for('hra'))


@app.route('/inventar')
def inventar_stranka():
    if 'jmeno_hrdiny' not in session:
        return redirect(url_for('index'))

    svet_data = nacti_svet()
    definice_predmetu = svet_data['predmety']
    hrdina = Hrdina(session['jmeno_hrdiny'], session['hrdina_hp'], session['hrdina_max_hp'])
    utok, obrana = hrdina.spocti_statistiky(session['inventar'], definice_predmetu)
    zprava = session.pop('inventar_zprava', None)

    return render_template(
        'inventar.html',
        inventar=session['inventar'],
        definice_predmetu=definice_predmetu,
        hp=session['hrdina_hp'],
        max_hp=session['hrdina_max_hp'],
        utok=utok,
        obrana=obrana,
        zprava=zprava,
        pocet_slotu=len(session['inventar']),
        max_slotu=MAX_SLOTS
    )


@app.route('/pouzi/<id_predmetu>')
def pouzi(id_predmetu):
    svet_data = nacti_svet()
    definice_predmetu = svet_data['predmety']

    if definice_predmetu.get(id_predmetu, {}).get("typ") == "lektvar":
        nove_hp, zprava = Inventar.pouzij_lektvar(
            id_predmetu, session['hrdina_hp'], session['hrdina_max_hp'], definice_predmetu
        )
        session['hrdina_hp'] = nove_hp
        session['inventar'].remove(id_predmetu)
        session['inventar_zprava'] = zprava
        session.modified = True

    return redirect(url_for('inventar_stranka'))


@app.route('/vyhod/<id_predmetu>')
def vyhod(id_predmetu):
    if id_predmetu in session['inventar']:
        session['inventar'].remove(id_predmetu)
        session['mapa_predmetu'][session['aktualni_lokace']].append(id_predmetu)
        session['inventar_zprava'] = "Předmět jsi vyhodil na zem."
        session.modified = True
    return redirect(url_for('inventar_stranka'))


# ── SOUBOJ ────────────────────────────────────────────────────────────────────

@app.route('/souboj')
def souboj():
    if 'aktualni_lokace' not in session:
        return redirect(url_for('index'))

    id_lokace = session['aktualni_lokace']
    svet_data = nacti_svet()
    id_nepritele = svet_data['lokace'][id_lokace]['nepritel']
    nepritel = session['nepratele'][id_nepritele]
    definice_predmetu = svet_data['predmety']

    hrdina = Hrdina(session['jmeno_hrdiny'], session['hrdina_hp'], session['hrdina_max_hp'])
    utok_hrdiny, obrana_hrdiny = hrdina.spocti_statistiky(session['inventar'], definice_predmetu)

    zprava = session.pop('zprava_souboj', "⚔️ Boj začíná!")

    # Lektvary dostupné v inventáři pro použití v souboji
    lektvary_v_inventari = [
        pid for pid in session['inventar']
        if definice_predmetu.get(pid, {}).get('typ') == 'lektvar'
    ]

    return render_template(
        'souboj.html',
        hp=session['hrdina_hp'],
        max_hp=session['hrdina_max_hp'],
        utok=utok_hrdiny,
        obrana=obrana_hrdiny,
        nepritel=nepritel,
        zprava=zprava,
        lektvary=lektvary_v_inventari,
        definice_predmetu=definice_predmetu
    )


@app.route('/pouzi_v_souboji/<id_predmetu>')
def pouzi_v_souboji(id_predmetu):
    """Použití léčiva přímo v souboji – nepřítel poté zaútočí (ztratil jsi tah)."""
    if 'aktualni_lokace' not in session:
        return redirect(url_for('index'))

    svet_data = nacti_svet()
    definice_predmetu = svet_data['predmety']
    id_lokace = session['aktualni_lokace']
    id_nepritele = svet_data['lokace'][id_lokace]['nepritel']
    nepritel = session['nepratele'][id_nepritele]

    if id_predmetu in session['inventar'] and definice_predmetu.get(id_predmetu, {}).get('typ') == 'lektvar':
        nove_hp, zprava_lektvaru = Inventar.pouzij_lektvar(
            id_predmetu, session['hrdina_hp'], session['hrdina_max_hp'], definice_predmetu
        )
        session['hrdina_hp'] = nove_hp
        session['inventar'].remove(id_predmetu)
        session.modified = True

        # Nepřítel zaútočí (hráč promarnil tah)
        hrdina = Hrdina(session['jmeno_hrdiny'], session['hrdina_hp'], session['hrdina_max_hp'])
        _, obrana_hrdiny = hrdina.spocti_statistiky(session['inventar'], definice_predmetu)
        dmg_do_hrdiny = vypocti_poskozeni(nepritel['utok'], obrana_hrdiny)
        session['hrdina_hp'] -= dmg_do_hrdiny

        if session['hrdina_hp'] <= 0:
            return redirect(url_for('konec', vysledek='prohra'))

        session['zprava_souboj'] = (
            f"💊 {zprava_lektvaru} Nepřítel využil tvého okamžiku slabosti "
            f"a udeřil za {dmg_do_hrdiny} DMG!"
        )
        session.modified = True

    return redirect(url_for('souboj'))


@app.route('/akce_souboj/<akce>')
def akce_souboj(akce):
    if 'aktualni_lokace' not in session:
        return redirect(url_for('index'))

    id_lokace = session['aktualni_lokace']
    svet_data = nacti_svet()
    id_nepritele = svet_data['lokace'][id_lokace]['nepritel']
    nepritel = session['nepratele'][id_nepritele]

    if akce == 'utek':
        session['aktualni_lokace'] = 'cela_start'
        session['herni_zprava'] = "Utekl jsi v panice zpět do cely."
        return redirect(url_for('hra'))

    if akce == 'utok':
        hrdina = Hrdina(session['jmeno_hrdiny'], session['hrdina_hp'], session['hrdina_max_hp'])
        utok_hrdiny, obrana_hrdiny = hrdina.spocti_statistiky(session['inventar'], svet_data['predmety'])

        # Hráč zaútočí
        dmg_do_nepritele = vypocti_poskozeni(utok_hrdiny, nepritel['obrana'])
        nepritel['hp'] -= dmg_do_nepritele
        session.modified = True

        if nepritel['hp'] <= 0:
            # Nepřítel poražen – loot drop
            drop_id = svet_data['nepratele'][id_nepritele].get('drop')
            zprava_lootu = ""
            if drop_id and len(session['inventar']) < MAX_SLOTS:
                session['inventar'].append(drop_id)
                nazev_dropu = svet_data['predmety'][drop_id]['nazev']
                zprava_lootu = f" Získal jsi: {nazev_dropu}!"

            if id_nepritele == 'magnat':
                # Vítězství zajišťuje jen odplutí, klíče spadnou
                session['herni_zprava'] = f"Porazil jsi Magnáta!{zprava_lootu} Nyní jdi na přístav a odpluj!"
                session.modified = True
                return redirect(url_for('hra'))

            session['herni_zprava'] = f"Nepřítel poražen!{zprava_lootu} Můžeš pokračovat."
            session.modified = True
            return redirect(url_for('hra'))

        # Nepřítel zaútočí zpět
        dmg_do_hrdiny = vypocti_poskozeni(nepritel['utok'], obrana_hrdiny)
        session['hrdina_hp'] -= dmg_do_hrdiny

        if session['hrdina_hp'] <= 0:
            return redirect(url_for('konec', vysledek='prohra'))

        session['zprava_souboj'] = (
            f"Udělil jsi {dmg_do_nepritele} DMG. "
            f"Nepřítel ti vrátil úder za {dmg_do_hrdiny} DMG."
        )
        session.modified = True
        return redirect(url_for('souboj'))

    return redirect(url_for('souboj'))


# ── KONEC HRY ─────────────────────────────────────────────────────────────────

@app.route('/konec/<vysledek>')
def konec(vysledek):
    session.clear()
    return render_template('konec.html', vysledek=vysledek)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
