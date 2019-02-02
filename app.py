from flask import Flask, Response, request, render_template, make_response
import flask_excel as excel
from search import Search
from openpyxl import Workbook
import openpyxl
import pyexcel

from rq import Queue

from worker import conn
from search import Search
from utils import count_words_at_url

import time
# fix dimensiones por la coma que hay se separan en dos valores distintos en el excel
app = Flask(__name__)

counter = 0

@app.route('/')
def homepage():
    return render_template('index.html', data=counter)

@app.route("/", methods=["POST"])
def getPlotCSV():
    print("1111111")

    q = Queue(connection=conn)
    first_job = q.enqueue(count_words_at_url, url)
    time.sleep(2)
    result = first_job.result
    print("miiii resultado:", result)

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
    if s.status == 0:
        # in case there was not enough time
        print("here we go again!")
        s.status = 1

        # s.find_products(s.last_url)

    output = make_response(openpyxl.writer.excel.save_virtual_workbook(s.workbook))
    output.headers["Content-Disposition"] = "attachment; filename=PortalI.xlsx"
    output.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


    return output

if __name__ == '__main__':
    excel.init_excel(app)
    app.run(debug=True, use_reloader=True)
    # app.run()
