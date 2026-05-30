# 🏝️ Útěk z tajemného ostrova

Textová dobrodružná hra ve Flasku. Hráč prozkoumává soukromý ostrov,
bojuje se strážemi, sbírá předměty a snaží se uniknout na motorovém člunu.

---

## 📖 O hře

Probudil ses v cele na tajném soukromém ostrově. Neznáš jméno svého věznitele,
ale víš jedno – **musíš odtud pryč**. Ostrov obývají ozbrojené stráže a sám
Magnát, který ostrov ovládá.

**Cíl hry:**
1. Najdi **přístupový flash disk** (v slepé uličce) – odemkne dveře do trezoru.
2. Pronikni do **pracovny Magnáta** a poraz ho v souboji.
3. Získej **klíče od člunu** (loot po Magnátovi).
4. Dojdi na **přístavní molo** a odpluj!

---

## 🗺️ Mapa světa (12 lokací)

```
[SLP.UL]--[Z.KRILO]           [PRACOVNA]
               |                   |
           [FONTANA]---[KANCELAR]---+
               |           |
[V.HALA]--[NADVORI]   [GARAZE]
               |           |
[  CELA]--[CHODBA ]---[ZAHRADA]--[PRISTAV]
```

| Lokace          | Popis                                  |
|-----------------|----------------------------------------|
| Cela            | Startovní lokace, naleziš trubku       |
| Jižní chodba    | Spojovací uzel                         |
| Hlavní nádvoří  | Elixír, vstup do vily                  |
| Východní zahrady| Dolary, přístup k přístavu a garážím   |
| Vstupní hala    | Hlídá Strážný (boss 1)                 |
| Garáže          | Hlídá Strážce (boss 2), taktická vesta |
| Přístavní molo  | ⛵ Cíl útěku                           |
| Fontána         | Elixír, přechod na západ               |
| Kancelář        | Dolary, přístup k trezoru              |
| Západní křídlo  | Přechod ke slepé uličce                |
| Slepá ulička    | 🔑 Flash disk (nutný pro trezor)       |
| Pracovna Magnáta| Finální boss, drop klíčů               |

---

## 🎒 Předměty

| Předmět            | Typ      | Efekt                         |
|--------------------|----------|-------------------------------|
| Zrezivělá trubka   | Zbraň    | +5 útok                       |
| Strážcův nůž       | Zbraň    | +10 útok (drop ze strážného)  |
| Taktická vesta     | Brnění   | +10 obrana                    |
| Energetický elixír | Lektvar  | +30 HP                        |
| Přístupový disk    | Klíčový  | Odemkne trezor Magnáta        |
| Klíče od člunu     | Klíčový  | Umožní odplutí (drop z Magnáta) |
| Dolar              | Ostatní  | –                             |

**Limit inventáře: 8 slotů**

---

## ⚔️ Nepřátelé

| Nepřítel        | HP | Útok | Obrana | Drop           |
|-----------------|----|------|--------|----------------|
| Strážný         | 35 | 12   | 2      | Strážcův nůž   |
| Strážce garáží  | 45 | 15   | 4      | Energetický elixír |
| Magnát (boss)   | 60 | 18   | 5      | Klíče od člunu |

---

## 🎮 Ovládání

- **Pohyb** – tlačítka Dopředu / Dozadu / Doleva / Doprava
- **Předměty** – tlačítko „Vzít" u předmětů na zemi
- **Batoh** – tlačítko „🎒 Batoh" – zde lze předměty použít nebo vyhodit
- **Souboj** – Zaútočit / Použít lektvar přímo v boji / Utéct
- **Útěk** – na přístavním molu s klíči od člunu klikni „ODPLOUT"

---

## 🔧 Instalace a spuštění

```bash
# 1. Nainstaluj závislosti
pip install -r requirements.txt

# 2. Spusť aplikaci
python app.py

# 3. Otevři prohlížeč
# http://127.0.0.1:5000
```

---

## 📦 Závislosti (requirements.txt)

- `flask` – webový framework
- `gunicorn` – produkční WSGI server

---

## 🗂️ Struktura projektu

```
hra/
├── app.py                  ← Flask routes, spuštění aplikace
├── game/
│   ├── __init__.py
│   ├── hrdina.py           ← třída Hrdina (atributy, statistiky)
│   ├── mapa.py             ← načítání dat světa, ASCII mapa
│   ├── souboj.py           ← výpočet poškození (s random)
│   └── inventar.py         ← třída Predmet, třída Inventar, MAX_SLOTS
├── data/
│   └── svet.json           ← lokace, předměty, nepřátelé (vč. dropů)
├── templates/
│   ├── index.html          ← úvodní obrazovka, zadání jména
│   ├── hra.html            ← hlavní herní obrazovka, pohyb, předměty
│   ├── souboj.html         ← soubojová obrazovka s HP bary
│   ├── inventar.html       ← batoh s detaily předmětů
│   └── konec.html          ← výhra / prohra
├── static/
│   └── style.css           ← terminálový styl (zelená na černé)
├── requirements.txt
└── README.md
```
