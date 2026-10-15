from io import BytesIO

import xlsxwriter

from database import Order


def build_buyers_excel(orders: list[Order]) -> bytes:
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})
    worksheet = workbook.add_worksheet("Список")

    header_format = workbook.add_format(
        {
            "bold": True,
            "font_name": "Arial",
            "font_size": 11,
            "font_color": "#FFFFFF",
            "bg_color": "#4472C4",
            "align": "center",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#D9E2F3",
        }
    )
    text_format = workbook.add_format(
        {
            "font_name": "Arial",
            "font_size": 11,
            "valign": "vcenter",
            "border": 1,
            "border_color": "#D9E2F3",
        }
    )
    birthdate_format = workbook.add_format(
        {
            "font_name": "Arial",
            "font_size": 11,
            "num_format": "@",
            "align": "center",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#D9E2F3",
        }
    )
    checkbox_format = workbook.add_format(
        {
            "checkbox": True,
            "align": "center",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#D9E2F3",
        }
    )

    headers = ["ФИО", "Пришёл", "Дата рождения", "Группа или вуз", "TG username"]
    worksheet.write_row(0, 0, headers, header_format)

    for row, order in enumerate(orders, start=1):
        username = f"@{order.telegram_username}" if order.telegram_username else ""

        worksheet.write(row, 0, order.full_name, text_format)
        worksheet.insert_checkbox(row, 1, False, checkbox_format)
        worksheet.write_string(row, 2, order.birthdate, birthdate_format)
        worksheet.write(row, 3, order.group_name, text_format)
        worksheet.write(row, 4, username, text_format)
        worksheet.set_row(row, 24)

    worksheet.set_row(0, 28)
    worksheet.set_column("A:A", 34)
    worksheet.set_column("B:B", 12)
    worksheet.set_column("C:C", 19)
    worksheet.set_column("D:D", 24)
    worksheet.set_column("E:E", 20)
    worksheet.freeze_panes(1, 0)
    worksheet.autofilter(0, 0, len(orders), len(headers) - 1)
    worksheet.hide_gridlines(2)

    worksheet.set_landscape()
    worksheet.fit_to_pages(1, 0)
    worksheet.set_margins(left=0.3, right=0.3, top=0.5, bottom=0.5)
    worksheet.repeat_rows(0)
    worksheet.print_area(0, 0, len(orders), len(headers) - 1)

    workbook.close()
    return output.getvalue()
