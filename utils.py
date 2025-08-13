import json
import os
import time
from typing import Any

import pandas as pd
from xlsxwriter import (
    Workbook,
    format
)


def file_to_dict(filename: str) -> dict:
    data: dict = pd.read_excel(filename).to_dict()
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
        employee_data["Bônus Total"] = employee_data["Dias Trabalhados"] * 12
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
    workbook: Workbook = Workbook(f"{dir_path}/bonificacao_{months[time.localtime().tm_mon - 1]}.xlsx")
    
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

    worksheet = workbook.add_worksheet("bonificação")

    cols_titles: list[str] = [str(key) for key in data[0].keys()]
    data_len: int = len(data.keys())

    for i in range(len(cols_titles)):
        worksheet.set_row(0, 30)
        worksheet.set_column(i, i, len(cols_titles[i]) + 5)

        worksheet.write(0, i, cols_titles[i], title_format)

    for i in range(data_len):
        for j in range(len(cols_titles)):
            if cols_titles[j] not in ["Funcionário", "Faltas de Caixa", "Dias Trabalhados"] and data[i][cols_titles[j]] != "N/A":
                worksheet.write(i + 1, j, data[i][cols_titles[j]], currency_format)
            else:
                worksheet.write(i + 1, j, data[i][cols_titles[j]], row_format)

    workbook.close()


def load_style() -> str:
    style: str = ""

    with open("./_internal/style.txt") as file:
        style = file.read()

        file.close()
    
    return style


def load_config() -> dict:
    config: dict = {}

    with open("./_internal/config.json") as file:
        config = json.load(file)

        file.close()

    return config


def write_config(config: dict):
    with open("./_internal/config.json", "w") as file:
        json_object: str = json.dumps(config, indent = 4)

        file.write(json_object)

        file.close()
