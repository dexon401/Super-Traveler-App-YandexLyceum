import requests
import sys
from datetime import datetime

TRANSPORT_API_KEY = "Ключ можно получить здесь: https://tech.yandex.ru/rasp/raspapi/"


TRANSPORT_TYPES = {
    "plane": "Cамолет",
    "train": "Поезд",
    "suburban": "Электричка",
    "bus": "Автобус",
    "water": "Водный транспорт",
    "helicopter": "Вертолет",
}


def get_schedule(src, dest, date):
    params = {
        "apikey": TRANSPORT_API_KEY,
        "from": src,
        "to": dest,
        "format": "json",
        "lang": "ru_RU",
        "date": date,
    }

    response = requests.get(
        "https://api.rasp.yandex-net.ru/v3.0/search/", params=params
    )
    if not response.ok:
        print(f"Ошибка HTTP {response.status_code}: {response.reason}")
        print("Ответ сервера:", response.text)
        sys.exit(1)

    data = response.json()

    result = []
    for segment in data["segments"]:
        transport_type = segment["thread"]["transport_type"]
        number = segment["thread"]["number"]
        title = segment["thread"]["short_title"]
        departure = datetime.fromisoformat(segment["departure"])
        arrival = datetime.fromisoformat(segment["arrival"])
        duration = segment["duration"]
        string_duration = f"{duration // 3600}ч {(duration % 3600) // 60}мин"
        
        result.append(
            f"{TRANSPORT_TYPES[transport_type]}\t{number}\t{title}\t{departure.strftime("%H:%M")}\t{arrival.strftime("%H:%M")}\t{string_duration}"
        )
    
    return result
