from flask import Flask, Response, request, make_response
import flask_excel as excel
from openpyxl import Workbook
import openpyxl
import pyexcel

from search import Search
# fix dimensiones por la coma que hay se separan en dos valores distintos en el excel

app = Flask(__name__)

@app.route('/')
def homepage():
    return """
    <h1>Inmobiliaria Aguayo </h1>
    <h2> Por hacer: </h2>
    <p>Falta, agregar link a columna de excel, ratios y encabezados </p>
    <p>Busqueda de links mejorada</p>
    <p>Cambiar estilos</p>
    <h2> ejemplos a ingresar: (por ahora el link siempre tiene que terminar con 'pg=1')</h2>
    <h3> https://www.portalinmobiliario.com/venta/departamento/jardin-del-este-vitacura-santiago-metropolitana?ca=3&ts=1&mn=2&or=&sf=1&sp=0&at=0&pg=1 </h3>
    <h3> https://www.portalinmobiliario.com/venta/sitio/las-condes-metropolitana?ca=3&ts=1&mn=2&or=&sf=1&sp=0&at=0&pg=1 </h3>
    <form method="POST">
        <input name="text">
        <input type="submit">
    </form>
    """

@app.route("/", methods=["POST"])
def getPlotCSV():
    text = request.form['text']
    url = str(text)
    s = Search()
    # https://www.portalinmobiliario.com/venta/casa/las-condes-metropolitana?ca=2&ts=1&mn=2&or=&sf=1&sp=0&at=0&pg=
    s.find_products(url)

    wb = Workbook()
    ws = wb.active
    ws.append([1,2,3,4,5,6,7])

    # sheet = pyexcel.Sheet(s.data)
    output = make_response(openpyxl.writer.excel.save_virtual_workbook(wb))
    output.headers["Content-Disposition"] = "attachment; filename=export.xlsx"
    output.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return output

if __name__ == '__main__':
    excel.init_excel(app)
    app.run(debug=True, use_reloader=True)
