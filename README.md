# Habit Tracker 🎯

Webová aplikace pro sledování a budování zdravých návyků.

## Instalace a spuštění

### Docker (doporučeno)
```bash
# 1. Vytvoř .env soubor z šablony
cp .env.example .env

# 2. Spusť Docker
docker compose up --build
```
Aplikace běží na http://localhost:5000

### Lokálně
```bash
# 1. Virtuální prostředí
python -m venv .venv
.\.venv\Scripts\activate  # Windows

# 2. Závislosti
pip install -r requirements.txt

# 3. Konfigurace
cp .env.example .env
# .env soubor se vytvářet automaticky (SQLite - žádná extra konfigurace)

# 4. Spuštění
python app.py
```
Aplikace běží na http://127.0.0.1:5000

## Technologie

- Flask + SQLAlchemy + SQLite
- Jinja2 makra pro jednoduché šablony
- Flask-Login pro autentizaci
- Docker pro kontainerizaci
- Docker Compose pro orchestraci


