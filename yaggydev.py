from flask import Flask, render_template, send_file

app = Flask(__name__)


@app.route("/")
def landing():
    return render_template('index.html')


@app.route("/backpacking")
def essay():
    return send_file('static/pdf/briefing.pdf', attachment_filename='briefing.pdf')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
