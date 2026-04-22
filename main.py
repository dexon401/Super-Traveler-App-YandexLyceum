import sys
import json
import os

from api_scripts import get_schedule
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
    def __init__(self, token):
        super().__init__()

        self.token = token
        self.setupUi(self)

        self.fromCBox.addItems([*map(lambda place: place["name"], PLACES)])
        self.toCBox.addItems([*map(lambda place: place["name"], PLACES)])
        
        self.dateEdit.setDate(datetime.now())

        self.showBtn.clicked.connect(self.on_show_btn_press)

    def on_show_btn_press(self):
        src = PLACES[self.fromCBox.currentIndex()]
        dest = PLACES[self.toCBox.currentIndex()]
        date = self.dateEdit.date().toPyDate().isoformat()

        if src == dest:
            return
        
        data = get_schedule(src["code"], dest["code"], date)
        
        self.textBrowser.setPlainText("\n".join(data))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    token = None
    try:
        with open("config/config.json", "r") as f:
            data = json.load(f)
            token = data.get("token")
    except Exception:
        token, ok = QInputDialog.getText(
            None, "Введите токен", "Введите свой OAuth-токен Яндекс Диска"
        )
        if ok and token:
            os.makedirs("config", exist_ok=True)
            with open("config/config.json", "w") as f:
                json.dump({"token": token}, f)
        else:
            print("Токен не введён, выход.")
            sys.exit(0)

    main_window = MainWindow(token)
    main_window.show()
    sys.exit(app.exec())
