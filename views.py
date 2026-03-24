import os

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLayout,
    QVBoxLayout,
    QFileDialog,
    QMessageBox
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
from utils import (
    create_excel_file, 
    file_to_dict, 
    load_config, 
    write_config
)


class HomeWidget(QWidget):
    def __init__(self):
        super().__init__()


        self.data: dict | None = None


        self.table: Table = Table()


        self.input_tray: InputTray = InputTray()

        self.input_tray.per_day_payment_input_box.input.editingFinished.connect(self.toggle_apply_button)
        self.input_tray.parcial_debt_amount_input_box.input.editingFinished.connect(self.toggle_apply_button)
        
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


    def draw_dialog(self, path: str):
        msg_box: QMessageBox = QMessageBox()

        msg_box.setEscapeButton(QMessageBox.StandardButton.Close)

        if os.path.exists(path):
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setText("Sucesso!")
            msg_box.setInformativeText(f"Arquivo exportado para: {path}")
        else:
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setText("Erro!")
            msg_box.setInformativeText(f"Erro ao exportar arquivo para: {path}")

        msg_box.exec()


    def on_accepted(self):
        if self.button_tray.file_dialog.fileMode() == QFileDialog.FileMode.ExistingFile:
            self.draw_table()

            self.button_tray.export_table_button.setDisabled(False)
        elif self.button_tray.file_dialog.fileMode() == QFileDialog.FileMode.Directory:
            dir_path: str = self.button_tray.file_dialog.selectedUrls()[0].path()

            create_excel_file(self.data if self.data is not None else {}, dir_path)
            self.draw_dialog(dir_path)


    def data_is_valid(self) -> bool:
        return self.input_tray.get_parcial_debt_amount_value() >= 0 and self.input_tray.get_per_day_payment_value() > 0
    

    def toggle_apply_button(self):
        self.input_tray.apply_button.setEnabled(self.data_is_valid())


    def apply_changes(self):
        config: dict = load_config()

        per_day_payment: float = self.input_tray.get_per_day_payment_value()
        parcial_debt_amount: int = self.input_tray.get_parcial_debt_amount_value()

        config["per_day_payment"] = per_day_payment if per_day_payment > 0 else 1
        config["parcial_debt_amount"] = parcial_debt_amount if parcial_debt_amount >= 0 else 0

        write_config(config)

        if self.data is not None:
            self.draw_table()


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setCentralWidget(HomeWidget())
