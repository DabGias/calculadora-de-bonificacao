from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLayout,
    QVBoxLayout,
    QFileDialog
)
from PySide6.QtCore import (
    QSortFilterProxyModel
)

from components import (
    ButtonTray,
    InputTray, 
    Table
)
from models import TableModel
from utils import create_excel_file, file_to_dict, load_config, write_config


class HomeWidget(QWidget):
    def __init__(self):
        super().__init__()


        self.data: dict | None = None


        self.table: Table = Table()


        self.input_tray: InputTray = InputTray()

        self.input_tray.apply_button.clicked.connect(self.apply_changes)


        self.button_tray: ButtonTray = ButtonTray()

        self.button_tray.export_table_button.setDisabled(True)

        self.button_tray.open_file_button.clicked.connect(self.button_tray.open_file)
        self.button_tray.export_table_button.clicked.connect(self.button_tray.open_dir)
        self.button_tray.file_dialog.accepted.connect(self.on_accepted) 


        layout: QLayout = QVBoxLayout()

        layout.addWidget(self.table)
        layout.addSpacing(20)
        layout.addWidget(self.input_tray)
        layout.addSpacing(20)
        layout.addWidget(self.button_tray)

        self.setLayout(layout)


    def draw_table(self):
        self.data = file_to_dict(self.button_tray.file_dialog.selectedFiles()[0])

        sort_filter_proxy: QSortFilterProxyModel = QSortFilterProxyModel()

        sort_filter_proxy.setSourceModel(TableModel(self.data))

        self.table.setModel(sort_filter_proxy)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)


    def on_accepted(self):
        if self.button_tray.file_dialog.fileMode() == QFileDialog.FileMode.ExistingFile:
            self.draw_table()

            self.button_tray.export_table_button.setDisabled(False)
        elif self.button_tray.file_dialog.fileMode() == QFileDialog.FileMode.Directory:
            dir_path: str = self.button_tray.file_dialog.selectedUrls()[0].path()

            create_excel_file(self.data if self.data is not None else {}, dir_path)


    def apply_changes(self):
        config: dict = load_config()

        config["per_day_payment"] = self.input_tray.get_per_day_payment_value()
        config["parcial_debt_amount"] = self.input_tray.get_parcial_debt_amount_value()

        write_config(config)

        if self.data is not None:
            self.draw_table()


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setCentralWidget(HomeWidget())
