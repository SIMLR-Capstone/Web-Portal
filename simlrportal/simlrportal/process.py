from flask import render_template, request, jsonify
from simlrportal import app, db
import os
import json

@app.route('/newprocess.html', methods=['GET'])
def render_newprocess():
    return render_template("newprocess.html")

@app.route('/installed-methods', methods=['GET', 'POST'])
def get_installed_methods():
    if request.method == "GET":
        type = request.args.get("type", "")
        name = request.args.get("name", "")
        package = request.args.get("name", "")
        if name == "_all":
            f = open(os.path.join("./simlrportal/installed-methods/" + type + ".json"), "r")
            read_json = f.read()
            f.close()
            return read_json
    return "failed", 404
