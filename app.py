from flask import Flask, jsonify, request
import os
import subprocess
import json

app = Flask(__name__)

@app.route("/")
def index():
    return "Welcome to the Data Analysis App!"

@app.route("/top10")
def top10():
    if not os.path.exists("sorted_data.json"):
        return "Data not sorted yet. Please update."
    with open("sorted_data.json", "r") as file:
        data = json.load(file)[:10]
    return jsonify(data)

@app.route("/search")
def search():
    query = request.args.get("query")
    if not query:
        return "Query not provided.", 400

    if not os.path.exists("sorted_data.json"):
        return "Data not available. Please update.", 400

    with open("sorted_data.json", "r") as file:
        data = json.load(file)

    results = [item for item in data if query.lower() in item["name"].lower() or str(item["id"]) == query]
    return jsonify(results)

@app.route("/update")
def update():
    try:
        subprocess.run(["python3", "data_generator.py"], check=True)
        subprocess.run(["./data_sorter"], check=True)
        return "Data updated successfully!"
    except subprocess.CalledProcessError as e:
        return f"Error during update: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)
