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
    text = request.form['text'] # url from webpage
    url = str(text)

    q = Queue(connection=conn)
    first_job = q.enqueue(count_words_at_url, url)
    result = first_job.result
    while not result:
        result = first_job.result

    print("miiii resultado:", result)

    output = make_response(openpyxl.writer.excel.save_virtual_workbook(result))
    output.headers["Content-Disposition"] = "attachment; filename=PortalI.xlsx"
    output.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


    return output

if __name__ == '__main__':
    excel.init_excel(app)
    app.run(debug=True, use_reloader=True)
    # app.run()
