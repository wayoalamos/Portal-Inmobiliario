from search import Search
from openpyxl import Workbook
from flask import make_response
import openpyxl
import pyexcel


def count_words_at_url(url, app):
    with app.app_context():
        print("dentro de la funcion")
        s = Search() # create search element
        s.workbook = Workbook() # create workbook element
        s.workbook_active = s.workbook.active

        # excel headers
        header=["Tipo", "Categoria", "Ubicacion", "Codigo", "Informacion",
        "Construido", "Terreno", "Valor(UF)", "UF/Construido", "UF/Terreno", "url"]
        s.workbook_active.append(header)

        # aca esta el problema
        s.find_products(url) # find products of the urls
        if s.status == 0:
            # in case there was not enough time
            print("here we go again!")
            s.status = 1

            # s.find_products(s.last_url)

        output = make_response(openpyxl.writer.excel.save_virtual_workbook(s.workbook))
        output.headers["Content-Disposition"] = "attachment; filename=PortalI.xlsx"
        output.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        print("terminando la funcion")
        return output
