import requests
import sys
from datetime import datetime

TRANSPORT_TYPES = {
    "plane": "Cамолет",
    "train": "Поезд",
    "suburban": "Электричка",
    "bus": "Автобус",
    "water": "Водный транспорт",
    "helicopter": "Вертолет",
}

PREC_TYPES = {
    "NO_TYPE": "Без осадков",
    "RAIN": "Дождь",
    "SLEET": "Снег с дождем",
    "SNOW": "Снег",
    "HAIL": "Град",
}


def get_schedule(src, dest, date, transport_key):
    params = {
        "apikey": transport_key,
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
        departure = datetime.fromisoformat(segment["departure"])
        arrival = datetime.fromisoformat(segment["arrival"])
        duration = segment["duration"]
        string_duration = (
            f"{round(duration // 3600)}ч {round((duration % 3600) // 60)}мин"
        )

        result.append(
            f"{TRANSPORT_TYPES[transport_type]}\t{number}\t{departure.strftime("%H:%M")}\t{arrival.strftime("%H:%M")}\t{string_duration}"
        )

    return result


def get_weather(lat, lon, date, weather_key):
    date = datetime.strptime(date, "%Y-%m-%d")
    days = date.day - datetime.now().day

    if days < 0 or days > 10:
        return None

    headers = {"X-Yandex-Weather-Key": weather_key}
    query = """
    {
        weatherByPoint(request: { lat: %f, lon: %f}) {
            forecast {
                days(limit: %d) {
                    parts {
                        day {
                            temperature
                            precType
                        }  
                    }
                }
            }
        }
    }
    """ % (
        lat,
        lon,
        days + 1,
    )
    response = requests.post(
        "https://api.weather.yandex.ru/graphql/query",
        headers=headers,
        json={"query": query},
    )
    forecast = response.json()["data"]["weatherByPoint"]["forecast"]["days"][-1][
        "parts"
    ]["day"]

    return [
        f"Осадки: {PREC_TYPES[forecast["precType"]]}",
        f"Температура: {forecast["temperature"]}",
    ]


def load_file_to_disk(content, oauth_key):
    headers = {"Authorization": oauth_key}
    params = {"path": "/result.txt", "overwrite": "true"}

    response = requests.get(
        "https://cloud-api.yandex.net/v1/disk/resources/upload",
        params=params,
        headers=headers,
    )
    if not response.ok:
        return False

    link = response.json()["href"]

    headers = {"content-type": "text/plain"}
    response = requests.put(link, content, headers=headers)
    return True
