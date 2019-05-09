"""
Andrew Shackelford
ashackelford@college.harvard.edu

Peter Chang
chang04@college.harvard.edu

CS 208 - Spring 2019
Final Project: A Modular System for Local Differential Privacy
"""

from flask import Flask, flash, redirect, render_template, request, session, url_for
import json
import sqlite3
import random
import string
import numpy as np
import os

app = Flask(__name__)

letters = string.ascii_lowercase

# check for correct path to DB due to limitations with Python Anywhere
if os.path.isfile('CS-208-Final-Project/Website/data.db'):
    db_path = 'CS-208-Final-Project/Website/data.db'
else:
    db_path = 'data.db'

# datasets
global_datasets = [{'id': 0, 'text': 'Who is your favorite professor? Salil (true), or James (false)?'},
            {'id': 1, 'text': 'Did you enjoy this course?'},
            {'id': 2, 'text': 'Do you like ice cream?'},
            {'id': 3, 'text': 'Population test (Debug Only)'}]

# parameters for the datasets
global_parameters = {0: {'total_epsilon_val' : 0.5,
                         'indiv_epsilon_val' : 0.5},
                     1: {'total_epsilon_val' : 1.,
                         'indiv_epsilon_val' : 0.5},
                     2: {'total_epsilon_val' : 10000000.,
                         'indiv_epsilon_val' : 10.},
                     3: {'total_epsilon_val' : 1.,
                         'indiv_epsilon_val' : 1.}}

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# route to choose a dataset to submit data to
@app.route("/choose_dataset", methods=["GET", "POST"])
def choose_dataset():
    if request.method == "POST":
        print "hi post"
        print request
        print request.form
        messages = request.form.to_dict(flat=False)
        print messages
        messages['id'] = int(messages['id'][0])
        return redirect(url_for('submit_data', messages=json.dumps(messages)))
    return render_template("choose_dataset.html", datasets=global_datasets)

# route to submit data to a single dataset
@app.route("/submit_data", methods=["GET", "POST"])
def submit_data():
    if request.method == "POST":
        # get submitted data
        messages = request.form.to_dict(flat=False)
        messages['was_successful'] = int(messages['was_successful'][0])
        messages['response'] = int(messages['response'][0])
        messages['dataset_id'] = messages['dataset_id'][0]
        # unique response ID so each person can identify their data in output
        # (mostly for demonstration purposes, not strictly necessary in production)
        messages['response_id'] = ''.join(random.choice(letters) for i in range(10))

        # if we have privacy budget left, submit it
        if messages['was_successful']:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("INSERT INTO results VALUES (?, ?, ?)", (messages['response_id'], messages['dataset_id'], messages['response']))
            conn.commit()
            conn.close()
            return redirect(url_for('success', messages=json.dumps(messages)))
        else:
            return redirect(url_for('failure'))
    else:
        # grab dataset and parameters
        dataset_id = json.loads(request.args['messages'])['id']
        parameters = global_parameters[dataset_id]
        dataset = global_datasets[dataset_id]
        return render_template("submit_data.html", dataset=dataset, parameters=parameters)


# debug route only to demonstrate how DP mean approaches population mean over time
@app.route("/submit_multiple_data", methods=["GET", "POST"])
def submit_multiple_data():
    if request.method == "POST":
        # get submitted data
        messages = request.form.to_dict(flat=False)
        messages['was_successful'] = int(messages['was_successful'][0])
        messages['response'] = int(messages['response'][0])
        messages['dataset_id'] = messages['dataset_id'][0]
        messages['response_id'] = ''.join(random.choice(letters) for i in range(10))

        # submit to database
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("INSERT INTO results VALUES (?, ?, ?)", (messages['response_id'], messages['dataset_id'], messages['response']))
        conn.commit()
        conn.close()

        return ""
    else:
        eps_one_datasets = []
        for dataset in global_datasets:
            if global_parameters[dataset['id']]['indiv_epsilon_val'] == 1:
                eps_one_datasets.append(dataset)
        return render_template("submit_multiple_data.html", datasets=eps_one_datasets)

# route to choose dataset from which to view data
@app.route("/view_dataset", methods=["GET", "POST"])
def view_dataset():
    if request.method == "POST":
        messages = request.form.to_dict(flat=False)
        messages['id'] = int(messages['id'][0])
        return redirect(url_for('view_data', messages=json.dumps(messages)))
    else:
        return render_template("view_dataset.html", datasets=global_datasets)

# calculate the scaled mean given responses
def calculate_scaled_mean(responses):
    if len(responses) == 0:
        return 0.

    epsilon = global_parameters[responses[0]['dataset_id']]['indiv_epsilon_val']
    vector = []
    for response in responses:
        vector.append(response['response'])
    scaled = np.mean(vector) * (np.exp(epsilon) + 1.) / (np.exp(epsilon) - 1.)
    return (scaled + 1.) / 2.

# route to view data from a single dataset
@app.route("/view_data", methods=["GET"])
def view_data():
    # get dataset
    dataset_id = json.loads(request.args['messages'])['id']
    dataset = global_datasets[dataset_id]

    # get data
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM results where dataset_id = ?", (dataset_id,))
    results = c.fetchall()
    conn.close()

    # format data for Jinja
    responses = []
    for result in results:
        responses.append({'response_id': result[0], 'dataset_id': result[1], 'response': result[2]})
    dataset['scaled_mean'] = calculate_scaled_mean(responses)

    return render_template("view_data.html", dataset=dataset, responses=responses)

# route for success on submitting data
@app.route("/success", methods=["GET"])
def success():
    messages = request.args['messages']
    return render_template("success.html", parameters=json.loads(messages))

# route for failure on submitting data
@app.route("/failure", methods=["GET"])
def failure():
    return render_template("failure.html")

