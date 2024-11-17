from flask import Flask, jsonify
import json

app = Flask(__name__)

# Helper function to load alignments from JSON file
def load_alignments():
    with open('alignments.json') as file:
        return json.load(file)


# Route to get the similarity by task title
@app.route('/similarity/<title>', methods=['GET'])
def get_similarity_by_title(title):
    alignments = load_tasks()
    # Search for the task with the specified title
    for alignment in alignments:
        if alignment['title'].lower() == title.lower():
            return f"{title} if due {alignment['similarity']}"
    # If task not found, return a 404 error
    return jsonify({"error": "Alignment not found"}), 404
@app.route('/')
def home():
    return 'Alignment tracker'
