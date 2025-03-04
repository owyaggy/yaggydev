from flask import Flask, render_template, send_file
import logging
import os

app = Flask(__name__)


@app.route("/")
def landing():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
