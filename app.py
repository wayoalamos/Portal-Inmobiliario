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
    text = request.form['text']
    url = str(text)
    s = Search()
    # https://www.portalinmobiliario.com/venta/casa/las-condes-metropolitana?ca=2&ts=1&mn=2&or=&sf=1&sp=0&at=0&pg=
    s.find_products(url)

    wb = Workbook()
    ws = wb.active
    for line in s.data:
        ws.append(line)

    # sheet = pyexcel.Sheet(s.data)
    output = make_response(openpyxl.writer.excel.save_virtual_workbook(wb))
    output.headers["Content-Disposition"] = "attachment; filename=export.xlsx"
    output.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return output

if __name__ == '__main__':
    excel.init_excel(app)
    app.run(debug=True, use_reloader=True)

 
