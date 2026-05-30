from flask import Flask, render_template, request, session, redirect, url_for
from game.mapa import nacti_svet, ziskej_mapu
from game.hrdina import Hrdina
from game.inventar import Inventar
from game.souboj import vypocti_poskozeni

app = Flask(__name__)
app.secret_key = 'super_tajny_klic_pro_epstein_island'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        jmeno = request.form.get('jmeno')
        if jmeno:
            session.clear()
            session['jmeno_hrdiny'] = jmeno
            session['aktualni_lokace'] = 'cela_start'
            session['inventar'] = []
            session['hrdina_hp'] = 100
            session['hrdina_max_hp'] = 100

            # Nastavení předmětů
            svet_data = nacti_svet()
            mapa_predmetu = {}
            for id_lokace, lokace_info in svet_data['lokace'].items():
                mapa_predmetu[id_lokace] = lokace_info['predmety_zde']
            session['mapa_predmetu'] = mapa_predmetu

            # Nastavení nepřátel
            session['nepratele'] = {
                'strazny': {'nazev': 'Strážný', 'hp': 30, 'utok': 12, 'obrana': 2},
                'magnat': {'nazev': 'Magnát', 'hp': 50, 'utok': 18, 'obrana': 5}
            }

            return redirect(url_for('hra'))
    return render_template('index.html')


@app.route('/hra')
def hra():
    if 'jmeno_hrdiny' not in session: return redirect(url_for('index'))

    svet_data = nacti_svet()
    id_lokace = session['aktualni_lokace']
    lokace_data = svet_data['lokace'].get(id_lokace)

    textova_mapa = ziskej_mapu(id_lokace)
    predmety_v_lokaci = session['mapa_predmetu'][id_lokace]
    definice_predmetu = svet_data['predmety']

    hrdina = Hrdina(session['jmeno_hrdiny'], session['hrdina_hp'], session['hrdina_max_hp'])
    utok, obrana = hrdina.spocti_statistiky(session['inventar'], definice_predmetu)

    zprava = session.pop('herni_zprava', None)

    return render_template('hra.html', jmeno=session['jmeno_hrdiny'], lokace=lokace_data, mapa=textova_mapa,
                           predmety_zde=predmety_v_lokaci, definice_predmetu=definice_predmetu,
                           hp=session['hrdina_hp'], max_hp=session['hrdina_max_hp'],
                           utok=utok, obrana=obrana, zprava=zprava)


@app.route('/jdi/<smer>')
def jdi(smer):
    if 'aktualni_lokace' not in session: return redirect(url_for('index'))
    svet_data = nacti_svet()
    aktualni_id = session['aktualni_lokace']
    lokace_data = svet_data['lokace'].get(aktualni_id)

    if lokace_data and smer in lokace_data['vychody']:
        nova_lokace_id = lokace_data['vychody'][smer]
        session['aktualni_lokace'] = nova_lokace_id

        #Pokud je v nové lokaci živý nepřítel, začíná boj
        nova_lokace_data = svet_data['lokace'].get(nova_lokace_id)
        id_nepritele = nova_lokace_data.get('nepritel')
        if id_nepritele and session['nepratele'][id_nepritele]['hp'] > 0:
            session['zprava_souboj'] = f"Cestu ti zablokoval {session['nepratele'][id_nepritele]['nazev']}!"
            return redirect(url_for('souboj'))

    return redirect(url_for('hra'))


#ROUTY PRO INVENTÁŘ
@app.route('/vezmi/<id_predmetu>')
def vezmi(id_predmetu):
    aktualni_id = session['aktualni_lokace']
    if id_predmetu in session['mapa_predmetu'][aktualni_id]:
        session['mapa_predmetu'][aktualni_id].remove(id_predmetu)
        session['inventar'].append(id_predmetu)
        session['herni_zprava'] = "Sebral jsi předmět."
        session.modified = True
    return redirect(url_for('hra'))


@app.route('/inventar')
def inventar_stranka():
    if 'jmeno_hrdiny' not in session: return redirect(url_for('index'))
    svet_data = nacti_svet()
    definice_predmetu = svet_data['predmety']
    hrdina = Hrdina(session['jmeno_hrdiny'], session['hrdina_hp'], session['hrdina_max_hp'])
    utok, obrana = hrdina.spocti_statistiky(session['inventar'], definice_predmetu)
    zprava = session.pop('inventar_zprava', None)
    return render_template('inventar.html', inventar=session['inventar'], definice_predmetu=definice_predmetu,
                           hp=session['hrdina_hp'], max_hp=session['hrdina_max_hp'], utok=utok, obrana=obrana,
                           zprava=zprava)


@app.route('/pouzi/<id_predmetu>')
def pouzi(id_predmetu):
    svet_data = nacti_svet()
    definice_predmetu = svet_data['predmety']
    if definice_predmetu.get(id_predmetu, {}).get("typ") == "lektvar":
        nove_hp, zprava = Inventar.pouzij_lektvar(id_predmetu, session['hrdina_hp'], session['hrdina_max_hp'],
                                                  definice_predmetu)
        session['hrdina_hp'] = nove_hp
        session['inventar'].remove(id_predmetu)
        session['inventar_zprava'] = zprava
        session.modified = True
    return redirect(url_for('inventar_stranka'))


@app.route('/vyhod/<id_predmetu>')
def vyhod(id_predmetu):
    session['inventar'].remove(id_predmetu)
    session['mapa_predmetu'][session['aktualni_lokace']].append(id_predmetu)
    session['inventar_zprava'] = "Vyhodil jsi předmět."
    session.modified = True
    return redirect(url_for('inventar_stranka'))


#SOUBOJ A KONEC HRY
@app.route('/souboj')
def souboj():
    if 'aktualni_lokace' not in session: return redirect(url_for('index'))

    id_lokace = session['aktualni_lokace']
    svet_data = nacti_svet()
    id_nepritele = svet_data['lokace'][id_lokace]['nepritel']
    nepritel = session['nepratele'][id_nepritele]

    hrdina = Hrdina(session['jmeno_hrdiny'], session['hrdina_hp'], session['hrdina_max_hp'])
    utok_hrdiny, obrana_hrdiny = hrdina.spocti_statistiky(session['inventar'], svet_data['predmety'])

    zprava = session.pop('zprava_souboj', "Boj začíná!")

    return render_template('souboj.html', hp=session['hrdina_hp'], max_hp=session['hrdina_max_hp'],
                           utok=utok_hrdiny, obrana=obrana_hrdiny, nepritel=nepritel, zprava=zprava)


@app.route('/akce_souboj/<akce>')
def akce_souboj(akce):
    id_lokace = session['aktualni_lokace']
    svet_data = nacti_svet()
    id_nepritele = svet_data['lokace'][id_lokace]['nepritel']
    nepritel = session['nepratele'][id_nepritele]

    if akce == 'utek':
        # Návrat na začátek
        session['aktualni_lokace'] = 'cela_start'
        session['herni_zprava'] = "Utekl jsi v panice zpět do cely."
        return redirect(url_for('hra'))

    if akce == 'utok':
        hrdina = Hrdina(session['jmeno_hrdiny'], session['hrdina_hp'], session['hrdina_max_hp'])
        utok_hrdiny, obrana_hrdiny = hrdina.spocti_statistiky(session['inventar'], svet_data['predmety'])

        # Hráč zaútočí
        dmg_do_nepritele = vypocti_poskozeni(utok_hrdiny, nepritel['obrana'])
        nepritel['hp'] -= dmg_do_nepritele

        if nepritel['hp'] <= 0:
            if id_nepritele == 'magnat':
                return redirect(url_for('konec', vysledek='vyhra'))  # Splněn cíl hry

            session['herni_zprava'] = f"Nepřítel poražen! Můžeš pokračovat."
            session.modified = True
            return redirect(url_for('hra'))

        # Nepřítel zaútočí
        dmg_do_hrdiny = vypocti_poskozeni(nepritel['utok'], obrana_hrdiny)
        session['hrdina_hp'] -= dmg_do_hrdiny

        if session['hrdina_hp'] <= 0:
            return redirect(url_for('konec', vysledek='prohra'))  # Smrt hrdiny

        session['zprava_souboj'] = f"Udělil jsi {dmg_do_nepritele} DMG. Nepřítel ti vrátil úder za {dmg_do_hrdiny} DMG."
        session.modified = True
        return redirect(url_for('souboj'))


@app.route('/konec/<vysledek>')
def konec(vysledek):
    session.clear()
    return render_template('konec.html', vysledek=vysledek)


if __name__ == '__main__':
    app.run(debug=True)