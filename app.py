from flask import Flask, Response
from datetime import datetime
from search import Search

app = Flask(__name__)

@app.route('/')
def homepage():
    the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")


    return """
    <h1>Hsellos heeeroku</h1>
    <a href="/getPlotCSV">Click me.</a>
    <p>It is currently {time}.</p>

    <img src="http://loremflickr.com/600/400" />
    """.format(time=the_time)

@app.route("/getPlotCSV")
def getPlotCSV():
    s = Search()
    url = 'https://www.portalinmobiliario.com/venta/casa/las-condes-metropolitana?ca=2&ts=1&mn=2&or=&sf=1&sp=0&at=0&pg='
    for i in range(4):
        a = str(i)
        print(a+"/156")
        url2 = url+a
        s.find_products(url2)
    # with open("outputs/Adjacency.csv") as fp:
    #     csv = fp.read()
    with open("portalinmobiliario.csv") as fp:
        csv = fp.read()
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=psrtalDs.csv"})



if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
