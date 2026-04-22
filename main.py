import sys
import json
import os

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QInputDialog
from UI.ui import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    token = None
    try:
        with open("config/config.json", "r") as file:
            data = json.load(file)
            token = data.get("token")
    except Exception:
        token, ok = QInputDialog.getText(
            None,
            "Введите токен",
            "Введите свой OAuth-токен Яндекс Диска"
        )
        if ok and token:
            os.makedirs("config", exist_ok=True)
            with open("config/config.json", "w") as f:
                json.dump({"token": token}, f)
        else:
            print("Токен не введён, выход.")
            sys.exit(0)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
