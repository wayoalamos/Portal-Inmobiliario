from flask import Flask, Response
from datetime import datetime
app = Flask(__name__)

@app.route('/')
def homepage():
    the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")

    return """
    <h1>Hello heroku</h1>
    <a href="/getPlotCSV">Click me.</a>
    <p>It is currently {time}.</p>

    <img src="http://loremflickr.com/600/400" />
    """.format(time=the_time)

@app.route("/getPlotCSV")
def getPlotCSV():
    # with open("outputs/Adjacency.csv") as fp:
    #     csv = fp.read()
    csv = '1,2,3\n4,5,6\n'
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=portalDs.csv"})



if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
