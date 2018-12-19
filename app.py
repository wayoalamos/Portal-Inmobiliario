from flask import Flask, Response, request
from search import Search

# fix dimensiones por la coma que hay se separan en dos valores distintos en el excel

app = Flask(__name__)

@app.route('/')
def homepage():
    return """
    <h1>Inmobiliaria Aguayo </h1>
    <h2> ejemplo: </h2>
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
    csv = s.data
    csv = csv.replace(",",".")
    csv = csv.replace("*#*",",")
    csv = csv.replace('"', '')
    csv = csv.replace(';', '.')
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=palabras.csv"})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
