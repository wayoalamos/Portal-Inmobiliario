from flask import Flask, Response, request, make_response, render_template
import flask_excel as excel
from openpyxl import Workbook
import openpyxl
import pyexcel

from search import Search
# fix dimensiones por la coma que hay se separan en dos valores distintos en el excel
app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route("/", methods=["POST"])
def getPlotCSV():
    text = request.form['text'] # url from webpage
    url = str(text)

    s = Search() # create search element
    s.workbook = Workbook() # create workbook element
    s.workbook_active = s.workbook.active

    # excel headers
    header=["Tipo", "Categoria", "Ubicacion", "Codigo", "Informacion",
    "Construido", "Terreno", "Valor(UF)", "UF/Construido", "UF/Terreno", "url"]
    s.workbook_active.append(header)

    # aca esta el problema
    s.find_products(url) # find products of the urls

    output = make_response(openpyxl.writer.excel.save_virtual_workbook(s.workbook))
    output.headers["Content-Disposition"] = "attachment; filename=export.xlsx"
    output.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return output

if __name__ == '__main__':
    excel.init_excel(app)
    # app.run(debug=True, use_reloader=True)
    app.run()
