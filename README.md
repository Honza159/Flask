# Útěk z tajemného ostrova

Textová adventura v Pythonu a Flasku. Školní projekt.

---

## Instalace a spuštění

Požadavky: Python 3.10+

```bash
# nainstaluj závislosti
pip install -r requirements.txt

# spusť hru
python app.py
```

Hra poběží na `http://localhost:5000`.

---

## O čem hra je

Hraješ za novináře, který vyšetřoval zločince Viktora Vaška. Magnáta provozujícího
pašování z soukromého ostrova. Přiblížil ses příliš k pravdě a Vašek tě nechal unést.

Probudíš se v zamčené cele. Na zdi je vzkaz od předchozího vězně Tomáše Hrubého,
který tu strávil 43 dní a schoval klíče od člunu i přístupový flash disk
v opuštěném křídle vily.

Cíl hry:

1. Najdi přístupový flash disk
2. Dostaň se do pracovny Viktora Vaška a poraz ho v souboji
3. Získej klíče od člunu
4. Dojdi na přístavní molo a odpluj

---

## Ovládání

Hra se ovládá výhradně klikáním na tlačítka v prohlížeči.

| Akce | Jak                                         |
|---|---------------------------------------------|
| Pohyb po mapě | Tlačítka Dopředu / Dozadu / Doleva / Doprava |
| Sebrat předmět | Tlačítko "Vzít" u předmětu na zemi          |
| Otevřít batoh | Tlačítko "Batoh" v horní části obrazovky    |
| Použít lektvar | V batohu klikni "Použít" u lektvaru         |
| Vyhodit předmět | V batohu klikni "Vyhodit"                   |
| Zaútočit v souboji | Tlačítko "Zaútočit"                         |
| Utéct ze souboje | Tlačítko "Utéct" tě vrátí do startovní cely |
| Odplout (výhra) | Na přístavním mole s klíči od člunu v batohu |

---

## Předměty

| Předmět | Typ | Efekt |
|---|---|---|
| Zrezivělá trubka | zbran | +5 útok |
| Strážcův nůž | zbran | +10 útok |
| Taktická vesta | brneni | +10 obrana |
| Energetický elixír | lektvar | +30 HP |
| Přístupový flash disk | klicovy | odemkne dveře do pracovny |
| Klíče od člunu | klicovy | umožní odplutí |

Limit batohu: 8 slotů.

---

## Nepřátelé

| Nepřítel | HP | Útok | Obrana | Drop           |
|---|---|---|---|----------------|
| Strážný | 35 | 12 | 2 | nůž            |
| Strážce garáží | 45 | 15 | 4 | elixír         |
| Viktor Vašek | 60 | 18 | 5 | Klíče od člunu |

---

## Použité knihovny

Viz `requirements.txt`.

| Knihovna | Účel |
|---|---|
| Flask | webový framework, routování, session, šablony (Jinja2) |

Standardní knihovny Pythonu: `json`, `os`, `random`.

---

## Struktura projektu

```
app.py              -- hlavní Flask aplikace, všechny routy
data/
  svet.json         -- data hry: lokace, předměty, nepřátelé
  img.png           -- vizuální obrázek mapy na papíře
game/
  hrdina.py         -- třída Hrdina (HP, statistiky)
  inventar.py       -- třída Inventar, MAX_SLOTS
  mapa.py           -- načítání světa, ASCII mapa
  souboj.py         -- výpočet poškození
templates/
  uvod.html         -- úvodní stránka (zadání jména)
  index.html        -- hlavní herní obrazovka
  souboj.html       -- soubojová obrazovka
  inventar.html     -- stránka batohu
  konec.html        -- výhra / prohra
static/
  style.css         -- styly
requirements.txt
README.md
```
