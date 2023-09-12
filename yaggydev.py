from flask import Flask, render_template, send_file
import logging

app = Flask(__name__)


@app.route("/")
def landing():
    print("test a debugging message")
    return render_template('index.html')


@app.route("/backpacking")
def essay():
    try:
        print("got this far?")
        return send_file('static/pdf/briefing.pdf', attachment_filename='briefing.pdf')
    except UserWarning as Argument:
        file = open("errors.txt", "a")
        file.write(str(Argument))
        file.close()


if __name__ == "__main__":
    app.run(host='0.0.0.0')
