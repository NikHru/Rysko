from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/features")
def comments():
    return render_template("features.html")

@app.route("/firma")
def firma():
    return render_template("firma.html")

#alebo "flask --app main run"
#   flask --app main run      --debug
if __name__ == "__main__":
    app.run(debug=True)