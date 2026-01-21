# Habit Tracker 🎯

Webová aplikace pro sledování a budování zdravých návyků.

## Instalace a spuštění

### Docker (doporučeno)
```bash
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
# Edituj .env se svými SQL Server credentials

# 4. Migrace databáze
flask db init
flask db migrate
flask db upgrade

# 5. Spuštění
python app.py
```
Aplikace běží na http://127.0.0.1:5000

## Technologie

- Flask + SQLAlchemy + SQL Server
- Flask-Migrate pro verzování databází
- Jinja2 makra pro jednoduché šablony
- Flask-Login pro autentizaci


