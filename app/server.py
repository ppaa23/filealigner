from flask import Flask, jsonify, render_template, request, json

app = Flask(__name__)

# Helper function to load alignments from JSON file
def load_alignments():
    with open('alignments.json') as file:
        return json.load(file)

# Save alignments to the JSON file
def save_alignments(data):
    with open('alignments.json', 'w') as file:
        json.dump(data, file, indent=4)

# --- Routes ---

# Home route
@app.route('/')
def home():
    return render_template('home.html', title="Alignment Tracker")

# Route to view all alignments (GET)
@app.route('/alignments', methods=['GET'])
def view_alignments():
    alignments = load_alignments()
    return render_template('alignments.html', alignments=alignments, title="View Alignments")

# Route to search alignments by title (GET)
@app.route('/similarity/<title>', methods=['GET'])
def get_similarity_by_title(title):
    alignments = load_alignments()
    for alignment in alignments:
        if alignment['title'].lower() == title.lower():
            return render_template('similarity.html', alignment=alignment, title="Alignment Similarity")
    return jsonify({"error": "Alignment not found"}), 404

# Route to create a new alignment (POST)
@app.route('/alignments/create', methods=['POST'])
def create_alignment():
    new_alignment = request.json
    alignments = load_alignments()
    alignments.append(new_alignment)
    save_alignments(alignments)
    return jsonify({"message": "Alignment created successfully!", "alignment": new_alignment}), 201

# --- AJAX Form Route ---
@app.route('/alignments/new', methods=['GET'])
def new_alignment_form():
    return render_template('new_alignment.html', title="New Alignment")

@app.route('/alignments/new', methods=['POST'])
def handle_new_alignment():
    title = request.form['title']
    similarity = request.form['similarity']
    alignments = load_alignments()
    new_alignment = {"title": title, "similarity": similarity}
    alignments.append(new_alignment)
    save_alignments(alignments)
    return jsonify({"message": "Alignment created successfully!", "alignment": new_alignment}), 201

# --- Start the Flask App ---
if __name__ == '__main__':
    app.run(debug=True)
