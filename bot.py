import os
import requests
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
ZONA = "America/Mexico_City"   # cambia por tu zona horaria
MONEDAS = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD"]

# Avisa de eventos que empiezan entre 20 y 40 minutos a partir de ahora
DESDE_MIN, HASTA_MIN = 20,40.

URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
eventos = requests.get(URL, timeout=20).json()
if not isinstance(eventos, list):
    raise SystemExit(f"Respuesta inesperada del calendario: {eventos}")

ahora = datetime.now(timezone.utc)
proximos = []
for e in eventos:
    if e.get("impact") == "High" and e.get("country") in MONEDAS:
        hora = datetime.fromisoformat(e["date"])
        if ahora + timedelta(minutes=DESDE_MIN) <= hora < ahora + timedelta(minutes=HASTA_MIN):
            proximos.append((hora, e))

proximos.sort(key=lambda x: x[0])

if proximos:
    texto = "⏰ Evento importante en unos 30 minutos\n\n"
    for hora, e in proximos:
        local = hora.astimezone(ZoneInfo(ZONA))
        texto += (
            f"{local:%H:%M} {e['country']} {e['title']} "
            f"(pron: {e.get('forecast') or '-'} | prev: {e.get('previous') or '-'})\n"
        )
    texto += "\nOjo: el spread y la volatilidad suelen subir alrededor del dato."
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": texto},
    )
    print("Aviso enviado:", r.status_code)
else:
    print("Sin eventos en la ventana.")
