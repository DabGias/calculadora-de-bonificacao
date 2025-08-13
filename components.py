import os
from PySide6.QtWidgets import (
    QTableView, 
    QWidget,
    QPushButton,
    QFileDialog,
    QHBoxLayout,
    QVBoxLayout,
    QLayout,
    QLineEdit,
    QLabel
)

from utils import load_config


class Table(QTableView):
    def __init__(self):
        super().__init__()


class Button(QPushButton):
    def __init__(self, text: str):
        super().__init__()

        self.setText(text)
        

class TextInput(QLineEdit):
    def __init__(self, placeholder: str | None = None):
        super().__init__()

        if placeholder is not None: self.setPlaceholderText(placeholder)


class InputBox(QWidget):
    def __init__(self, label_txt: str, input_placeholder: str):
        super().__init__()


        self.label: QLabel = QLabel(label_txt)


        self.input: TextInput = TextInput(input_placeholder)


        layout: QLayout = QVBoxLayout()

        layout.addWidget(self.label)
        layout.addWidget(self.input)

        self.setLayout(layout)


class InputTray(QWidget):
    def __init__(self):
        super().__init__()


        config: dict = load_config()


        self.per_day_payment_input_box: InputBox = InputBox("Pagamento por Dia", "Ex.: 12,00")

        self.per_day_payment_input_box.input.setText("{:.2f}".format(config["per_day_payment"]).replace(".", ","))


        self.parcial_debt_amount_input_box: InputBox = InputBox("Faltas com desconto", "Ex.: 2")

        self.parcial_debt_amount_input_box.input.setText(str(config["parcial_debt_amount"]))


        self.apply_button: Button = Button("Aplicar")


        layout: QLayout = QHBoxLayout()

        layout.addWidget(self.per_day_payment_input_box)
        layout.addWidget(self.parcial_debt_amount_input_box)
        layout.addWidget(self.apply_button)

        self.setLayout(layout)


    def get_per_day_payment_value(self) -> float:
        return float(self.per_day_payment_input_box.input.text().replace(",", "."))
    

    def get_parcial_debt_amount_value(self) -> int:
        return int(self.parcial_debt_amount_input_box.input.text())


class ButtonTray(QWidget):
    def __init__(self):
        super().__init__()


        self.open_file_button: Button = Button("Abrir Arquivo")


        self.export_table_button: Button = Button("Exportar Tabela")


        self.file_dialog: QFileDialog = QFileDialog(
            self,
            directory = os.getcwd()
        )


        layout: QLayout = QHBoxLayout()

        layout.addWidget(self.open_file_button)
        layout.addWidget(self.export_table_button)

        self.setLayout(layout)


    def open_file(self):
        self.file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        self.file_dialog.setNameFilter("*.xlsx *.xls *.csv *.ods")

        self.file_dialog.open()


    def open_dir(self):
        self.file_dialog.setFileMode(QFileDialog.FileMode.Directory)
        self.file_dialog.setNameFilter("Any directory")

        self.file_dialog.open()
