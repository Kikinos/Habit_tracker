# Habit Tracker 🎯

Webová aplikace pro sledování a budování zdravých návyků. Postav si své návyky a sleduj svůj pokrok!

## Funkce

- 👤 **Uživatelské účty** - Registrace a přihlášení
- 📝 **Správa návyků** - Přidávání a mazání návyků
- 🎯 **Cílení** - Nastavení cíle pro každý návyk (1-7x týdně)
- ✅ **Denní sledování** - Označování splněných návyků
- 📊 **Statistiky** - Podrobná analýza pokroku (série, kalendár, etc.)
- 🎨 **Moderní design** - Responzivní rozhraní s animacemi

## Technologie

- **Backend:** Flask + SQLAlchemy + SQLite
- **Frontend:** HTML/CSS/JavaScript
- **Autentizace:** Flask-Login + Werkzeug
- **Python:** 3.10+

## Instalace

### Varianta 1: Docker Compose (doporučeno)

Stačí mít nainstalován Docker a Docker Compose.

```bash
git clone <repo-url>
cd projektik
docker compose up --build
```

Aplikace bude dostupná na: **http://localhost:5000**

Databáze se vytvoří automaticky.

### Varianta 2: Lokální spuštění

1. Klonuj repozitář
```bash
git clone <repo-url>
cd projektik
```

2. Vytvoř virtuální prostředí
```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. Nainstaluj závislosti
```bash
pip install -r requirements.txt
```

4. Spusť aplikaci
```bash
python app.py
```

Otevři prohlížeč na: **http://127.0.0.1:5000**

Databáze se vytvoří automaticky při spuštění.

## Struktura projektu

```
projektik/
├── app.py                 # Hlavní Flask aplikace
├── requirements.txt       # Python závislosti
├── Dockerfile            # Docker image definice
├── docker-compose.yml    # Docker Compose konfigurace
├── perf_test.py          # Performance testování
├── README.md             # Tento soubor
├── habits.db             # SQLite databáze (vytvoří se automaticky)
├── templates/
│   ├── index.html        # Domovská stránka
│   ├── login.html        # Přihlášení
│   ├── register.html     # Registrace
│   └── statistics.html   # Statistiky
└── static/
    └── style.css         # Styly
```

## Použití

1. **Registrace:** Vytvoř si nový účet
2. **Přihlášení:** Přihlas se pomocí username a hesla
3. **Přidej návyk:** Zadej název a cíl (kolikrát za týden)
4. **Sleduj pokrok:** Označuj splněné návyky
5. **Prohlédni si statistiky:** Viz svůj pokrok za poslední měsíc

## Bezpečnost

- ✅ Hesla hashovaná (Werkzeug)
- ✅ Session management (Flask-Login)
- ✅ Validace vstupů
- ✅ Izolace dat per user

## Poznámky

Toto je školní projekt určený pro lokální použití. Není optimalizováno pro produkční nasazení na internetu.

## Autor

Vytvořeno jako školní projekt

## Licence

MIT

## Performance testování

Pro otestování výkonu aplikace použijte skript `perf_test.py`:

1. Ujistěte se, že aplikace běží (např. přes Docker Compose na http://localhost:5000 nebo lokálně).
2. Spusťte performance tester:

```bash
python perf_test.py
```

Skript odešle paralelně 10 vláken s 50 požadavky na aplikaci a vypíše časy odezvy.

**Parametry lze upravit přímo v souboru:**
- `THREADS` - počet paralelních vláken
- `REQUESTS_PER_THREAD` - počet požadavků na vlákno
- `URL` - adresa aplikace
