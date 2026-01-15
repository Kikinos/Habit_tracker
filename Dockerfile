# Používáme oficiální Python image jako základ
FROM python:3.11-slim

# Nastavíme pracovní adresář
WORKDIR /app

# Zkopírujeme requirements a nainstalujeme závislosti
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Zkopírujeme zbytek aplikace
COPY . .

# Nastavíme proměnnou prostředí pro Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Otevřeme port 5000
EXPOSE 5000

# Spustíme aplikaci
CMD ["flask", "run"]
