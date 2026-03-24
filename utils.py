import json
import platform
import time
import getpass
import os

from pandas import read_excel
from xlsxwriter import (
    Workbook,
    format
)


def file_to_dict(filename: str) -> dict:
    data: dict = read_excel(filename).to_dict()
    config: dict = load_config()

    data_dict: dict = {}
    data_len: int = len(data["Movimento"])
    employees: list[str] = []
    debt_threshold: float = -10.00
    per_day_payment: float = float(config["per_day_payment"])
    parcial_debt_amount: int = int(config["parcial_debt_amount"])

    for i in range(data_len):
        employee: str = data["Fun. Responsável"][i]
        date: str = data["Movimento"][i]
        debt: float  = float(str(data["Diferença"][i]).replace("R$", "").replace(",", ".").replace(" ", ""))

        if employee not in employees:
            index: int = len(employees)

            data_dict[index] = {
                "Funcionário": employee,
                "R$/Dia": per_day_payment,
                "Faltas de Caixa": 0,
                "Primeira Falta": 0,
                "Segunda Falta": 0,
                "Demais Faltas": 0,
                "Dias Trabalhados": [date],
                "Bônus Total": 0,
                "Débito": [],
                "Total a Pagar": 0
            }

            employees.append(data["Fun. Responsável"][i])

            if debt < debt_threshold: 
                data_dict[index]["Débito"].append(debt)
        else:
            employee_index: int = employees.index(employee)

            if date not in data_dict[employee_index]["Dias Trabalhados"]:
                data_dict[employee_index]["Dias Trabalhados"].append(date)
            
            if debt < debt_threshold:
                data_dict[employee_index]["Débito"].append(debt)

    for index in data_dict:
        employee_data: dict = data_dict[index]

        employee_data["Faltas de Caixa"] = len(employee_data["Débito"])
        employee_data["Dias Trabalhados"] = len(employee_data["Dias Trabalhados"])
        employee_data["Bônus Total"] = employee_data["Dias Trabalhados"] * employee_data["R$/Dia"]

        #TODO: Adicionar lógica para número de faltas personalizado
        employee_data["Primeira Falta"] = employee_data["Débito"][0] if len(employee_data["Débito"]) != 0 else "N/A"
        employee_data["Segunda Falta"] = employee_data["Débito"][1] if len(employee_data["Débito"]) > 1 else "N/A"
        employee_data["Demais Faltas"] = sum(employee_data["Débito"][2:]) if len(employee_data["Débito"]) > 2 else "N/A"

        employee_data["Débito"] = round(sum(employee_data["Débito"]), 2) if len(employee_data["Débito"]) > parcial_debt_amount else round((sum(employee_data["Débito"]) / 2), 2)
        employee_data["Total a Pagar"] = employee_data["Débito"] + (employee_data["Dias Trabalhados"] * per_day_payment)

    return data_dict


def create_excel_file(data: dict, dir_path: str):
    months: tuple = (
        "janeiro",
        "fevereiro",
        "março",
        "abril",
        "maio",
        "junho",
        "julho",
        "agosto",
        "setembro",
        "outubro",
        "novembro",
        "dezembro"
    )
    workbook: Workbook = Workbook(f"{dir_path}/bonificacao_{months[time.localtime().tm_mon - 1] if time.localtime().tm_mon - 1 >= 0 else 0}.xlsx")
    
    row_format: format.Format = workbook.add_format()

    row_format.set_align("left")
    row_format.set_align("vcenter")

    currency_format: format.Format = workbook.add_format({
        "num_format": "[Blue]R$#.###,##;[Red]-R$#.###,##;R$0",
    })

    currency_format.set_align("left")
    currency_format.set_align("vcenter")

    title_format: format.Format = workbook.add_format({ 
        "bold": True, 
        "bg_color": "#1c1c1c", 
        "font_color": "#c1c1c1" 
    })

    title_format.set_align("center")
    title_format.set_align("vcenter")

    bonus_worksheet = workbook.add_worksheet("bonificação")
    receipts_worksheet = workbook.add_worksheet("recibos")

    cols_titles: list[str] = [str(key) for key in data[0].keys()]

    cols_titles_len: int = len(cols_titles)
    data_len: int = len(data.keys())

    for i in range(cols_titles_len):
        bonus_worksheet.set_row(0, 30)
        bonus_worksheet.set_column(i, i, len(cols_titles[i]) + 5)

        bonus_worksheet.write(0, i, cols_titles[i], title_format)

    receipt_strs: list[str] = [
        "RECIBO DE PAGAMENTO DE PREMIAÇÃO DE CAIXA",
        "COLABORADOR: ",
        "VALOR: R$",
        "DATA: ",
        "ASSINATURA DO COLABORADOR: "
    ]

    for i in range(data_len):
        employee_name: str = data[i]["Funcionário"]
        employee_total_payment: str = data[i]["Total a Pagar"]
        index: int = (i + 1) * (len(receipt_strs) + 1)

        receipts_worksheet.write((index - 5), 0, receipt_strs[0], title_format)

        receipts_worksheet.set_column((index - 5), 0, (len(receipt_strs[0]) + 10))

        receipts_worksheet.write((index - 4), 0, receipt_strs[1] + f"{employee_name.title()}", row_format)
        receipts_worksheet.write((index - 3), 0, receipt_strs[2] + f"{employee_total_payment:.2f}", row_format)
        receipts_worksheet.write((index - 2), 0, receipt_strs[3] + f"{time.localtime().tm_mday}/{time.localtime().tm_mon}/{time.localtime().tm_year}", row_format)
        receipts_worksheet.write((index - 1), 0, receipt_strs[4], row_format)

        for j in range(cols_titles_len):
            if cols_titles[j] not in ["Funcionário", "Faltas de Caixa", "Dias Trabalhados"] and data[i][cols_titles[j]] != "N/A":
                bonus_worksheet.write(i + 1, j, data[i][cols_titles[j]], currency_format)
            else:
                bonus_worksheet.write(i + 1, j, data[i][cols_titles[j]], row_format)

    workbook.close()


def setup_data_path(path: str):
    split_path: list[str] = [dir for dir in path.split("/") if dir != ""]
    temp_path: str = f"/{split_path[0]}" if platform.system() == "Linux" else split_path[0]
    
    for i in range(1, len(split_path)):
        temp_path += f"/{split_path[i]}"

        if not os.path.exists(temp_path): os.mkdir(temp_path)
        

def get_data_path() -> str:
    path: str = f"/home/{getpass.getuser()}/.config/Calculadora de Bonificação/" if platform.system() == "Linux" else f"{os.getenv("SystemDrive")}/Program Files/Calculadora de Bonificação/"

    if not os.path.exists(path): 
        setup_data_path(path)

    return path


def setup_stylesheet():  
    path: str = get_data_path()

    with open(path + "style.txt", "w") as file:
        file.write("""
QTableView {
    background-color: #222222;
}

QPushButton {
    color: green;
    padding: 10px;
    border-style: solid;
    border-color: green;
    border-width: 3px;
    border-radius: 10px;
    font: bold;
}

QPushButton:hover {
    color: white;
    background-color: green;
}
                
QPushButton:!enabled {
    color: gray;
    border-color: gray;      
}
        """)

        file.close()


def load_stylesheet() -> str:
    path: str = get_data_path()
    style: str = ""

    try:
        with open(path + "style.txt") as file:
            style = file.read()

            file.close()
    except FileNotFoundError:
        setup_stylesheet()
        
        with open(path + "style.txt") as file:
            style = file.read()

            file.close()
    
    return style


def setup_config():
    path: str = get_data_path()

    with open(path + "config.json", "w") as file:
        json_object: str = json.dumps(
            {
                "per_day_payment": 12.0,
                "parcial_debt_amount": 2
            }
        , indent = 4)

        file.write(json_object)

        file.close()


def load_config() -> dict:
    path: str = get_data_path()
    config: dict = {}

    try:
        with open(path + "config.json") as file:
            config = json.load(file)

            file.close()
    except FileNotFoundError:
        setup_config()

        with open(path + "config.json") as file:
            config = json.load(file)

            file.close()

    return config


def write_config(config: dict):
    path: str = get_data_path()

    with open(path + "config.json", "w") as file:
        json_object: str = json.dumps(config, indent = 4)

        file.write(json_object)

        file.close()
