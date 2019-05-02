from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)

datasets = [{'id': 0, 'text': 'text_0'},
            {'id': 1, 'text': 'text_1'},
            {'id': 2, 'text': 'text_2'}]

parameters = {'epsilon' : 1.}

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/submit_data", methods=["GET", "POST"])
def submit_data():
    if request.method == "POST":
        print "hi"
        print request
    return render_template("submit_data.html", datasets=datasets, parameters=parameters)