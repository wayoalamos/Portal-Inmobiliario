from flask import Flask, Response, request, render_template
import flask_excel as excel

from rq import Queue

from worker import conn
from search import Search
from utils import count_words_at_url
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
    result = q.enqueue(count_words_at_url, url)
    print("mi resultado:", result)

    return result

if __name__ == '__main__':
    excel.init_excel(app)
    app.run(debug=True, use_reloader=True)
    # app.run()
