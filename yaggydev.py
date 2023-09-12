from flask import Flask, render_template, send_file

app = Flask(__name__)


@app.route("/")
def landing():
    print("test a debugging message")
    return render_template('index.html')


@app.route("/backpacking")
def essay():
    print("got this far?")
    return send_file('static/pdf/briefing.pdf', attachment_filename='briefing.pdf')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
