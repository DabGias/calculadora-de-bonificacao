import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from utils import load_stylesheet
from views import AppWindow


def main():
    app: QApplication = QApplication(sys.argv)
    stylesheet: str = load_stylesheet()

    app.setApplicationDisplayName("Calculadora de Bonificação")
    app.setApplicationName("Calculadora de Bonificação")
    app.setStyleSheet(stylesheet)

    app_view: AppWindow = AppWindow()

    width: int = 1200
    height: int = 600
    x_pos: int = app_view.screen().geometry().center().x() - int(width / 2)
    y_pos: int = app_view.screen().geometry().center().y() - int(height / 2)

    app_view.setWindowTitle("Calculadora de Bonificação")
    app_view.setWindowIcon(QIcon("icon.png"))
    app_view.setGeometry(x_pos, y_pos, width, height)

    app_view.show()

    app.exec()


if __name__ == "__main__":
    main()
