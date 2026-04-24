import sys
import json
import os

from api_scripts import get_schedule, get_weather, load_file_to_disk
from datetime import datetime

from PyQt6.QtWidgets import QApplication, QMainWindow, QInputDialog
from UI.ui import Ui_MainWindow


PLACES = [
    {
        "name": "Москва",
        "code": "c213",
        "lat_lon": [55.753903, 37.620358],
    },
    {
        "name": "Санкт-Петербург",
        "code": "c2",
        "lat_lon": [59.931117, 30.360770],
    },
    {
        "name": "Новосибирск",
        "code": "c146",
        "lat_lon": [55.008352, 82.935733],
    },
    {
        "name": "Екатеринбург",
        "code": "c54",
        "lat_lon": [56.838926, 60.605702],
    },
    {
        "name": "Казань",
        "code": "c146",
        "lat_lon": [55.796127, 49.106405],
    },
    {
        "name": "Нижний Новгород",
        "code": "c47",
        "lat_lon": [56.296503, 43.936059],
    },
]


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, token, weather_api_key, transport_api_key):
        super().__init__()

        self.token = token
        self.weather_key = weather_api_key
        self.transport_key = transport_api_key

        self.setupUi(self)

        self.fromCBox.addItems([*map(lambda place: place["name"], PLACES)])
        self.toCBox.addItems([*map(lambda place: place["name"], PLACES)])

        self.dateEdit.setDate(datetime.now())

        self.showBtn.clicked.connect(self.on_show_btn_press)
        self.saveBtn.clicked.connect(self.on_save_btn_press)

    def on_show_btn_press(self):

        src = PLACES[self.fromCBox.currentIndex()]
        dest = PLACES[self.toCBox.currentIndex()]
        date = self.dateEdit.date().toPyDate().isoformat()

        if src == dest:
            return

        schedule = get_schedule(src["code"], dest["code"], date, self.transport_key)
        self.textBrowser.setPlainText("\n".join(schedule))
        weather = get_weather(*dest["lat_lon"], date, self.weather_key)

        if not weather:
            self.weather0.setText(
                "Погода доступна только на сегодня и на десять дней вперёд."
            )
            self.weather1.clear()
            self.weather2.clear()
        else:
            self.weather0.setText(f"Погода в {dest["name"]}:")
            self.weather1.setText(weather[0])
            self.weather2.setText(weather[1])

    def on_save_btn_press(self):
        text = self.textBrowser.toPlainText()
        if not text:
            return

        result = load_file_to_disk(text, self.token)
        if result:
            self.statusbar.showMessage("Успешно сохранено на Яндекс Диск!")
        else:
            with open("result.txt", "w") as file:
                file.write(text)
            self.statusbar.showMessage(
                "Провал сохранения на Яндекс Диск! Файл был сохранен локально."
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    token = None
    weather_api_key = None
    transport_api_key = None
    try:
        with open("config/config.json", "r") as f:
            data = json.load(f)
            token = data.get("token")
            weather_api_key = data.get("weather")
            transport_api_key = data.get("transport")
    except Exception:
        token, token_ok = QInputDialog.getText(
            None, "Введите токен", "Введите свой OAuth-токен Яндекс Диска"
        )
        weather_api_key, weather_ok = QInputDialog.getText(
            None, "Введите ключ", "Введите ключ API Яндекс Погоды"
        )
        transport_api_key, transport_ok = QInputDialog.getText(
            None, "Введите ключ", "Введите ключ API Яндекс Расписания"
        )
        if (
            token_ok
            and token
            and weather_ok
            and weather_api_key
            and transport_ok
            and transport_api_key
        ):
            os.makedirs("config", exist_ok=True)
            with open("config/config.json", "w") as f:
                json.dump(
                    {
                        "token": token,
                        "weather": weather_api_key,
                        "transport": transport_api_key,
                    },
                    f,
                )
        else:
            print("Данные введены неправильно!")
            sys.exit(0)

    main_window = MainWindow(token, weather_api_key, transport_api_key)
    main_window.show()
    sys.exit(app.exec())
