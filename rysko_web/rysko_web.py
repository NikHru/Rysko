from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/comments")
def comments():
    return render_template("comments.html")

@app.route("/try")
def notebook():
    return render_template("try.html")


#alebo "flask --app main run"
#                                 --debug
if __name__ == "__main__":
    app.run(debug=True)