from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/features")
def features():
    return render_template("features/index.html")

@app.route("/firma")
def firma():
    return render_template("firma/index.html")

#alebo "flask --app main run"
#   flask --app main run      --debug
if __name__ == "__main__":
    app.run(debug=True)