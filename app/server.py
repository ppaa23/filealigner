import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from alignment import perform_alignment  # Alignment logic moved to a separate file

app = Flask(__name__)
app.secret_key = "YOUR_SECRET_KEY_HERE"

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model for user
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

# Database model for alignment history
class AlignmentHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    file1_name = db.Column(db.String(120), nullable=False)
    file2_name = db.Column(db.String(120), nullable=False)
    similarity = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    alignment_id = db.Column(db.String(36), unique=True, nullable=False)

with app.app_context():
    db.create_all()

def current_user():
    """Retrieve the currently logged-in user."""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

@app.route('/')
def index():
    """Landing page."""
    if current_user():
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash("Username already exists. Please choose another one.", "error")
            return render_template('register.html')

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        return redirect(url_for('home'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log in a user."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password.", "error")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Log out the current user."""
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/home')
def home():
    """Home page for logged-in users."""
    if not current_user():
        return redirect(url_for('login'))
    return render_template('based/home.html', current_user=current_user())

@app.route('/tools/multialign', methods=['GET', 'POST'])
def multialign():
    """Multiple alignment page."""
    if not current_user():
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Retrieve uploaded files
        files = request.files.getlist('files')
        if not files or len(files) < 2:
            flash("Please upload at least two files for alignment.", "error")
            return redirect(url_for('multialign'))

        # Perform multiple alignment (placeholder logic)
        flash("Multiple alignment performed successfully!", "success")
        return redirect(url_for('history'))

    return render_template('based/multialign.html')

@app.route('/tools/pairwise', methods=['GET', 'POST'])
def align():
    """Handle pairwise alignment."""
    if not current_user():
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Retrieve uploaded files
        file1 = request.files.get('file1')
        file2 = request.files.get('file2')

        if not file1 or not file2:
            flash("Please upload two files for alignment.", "error")
            return redirect(url_for('align'))

        # Perform alignment
        alignment_result = perform_alignment(file1.read().decode('utf-8', errors='replace'),
                                             file2.read().decode('utf-8', errors='replace'))

        # Save alignment history
        alignment_id = str(uuid.uuid4())
        alignment = AlignmentHistory(
            user_id=session['user_id'],
            file1_name=file1.filename,
            file2_name=file2.filename,
            similarity=alignment_result['similarity'],
            alignment_id=alignment_id
        )
        db.session.add(alignment)
        db.session.commit()

        # Pass results to the results page
        return render_template('based/results.html', similarity=alignment_result['similarity'],
                               aligned_file1=alignment_result['aligned_file1'],
                               aligned_file2=alignment_result['aligned_file2'])

    return render_template('based/align.html')

@app.route('/results/p/<alignment_id>')
def alignment_results(alignment_id):
    """Display the results of a specific alignment."""
    if not current_user():
        return redirect(url_for('login'))

    # Find the alignment in the database
    alignment = AlignmentHistory.query.filter_by(alignment_id=alignment_id, user_id=session['user_id']).first()
    if not alignment:
        flash("Result not found.", "error")
        return redirect(url_for('history'))

    # Simulate the aligned content (if not stored previously)
    aligned_file1 = "Aligned content for file 1"
    aligned_file2 = "Aligned content for file 2"

    return render_template('based/results.html', similarity=alignment.similarity,
                           aligned_file1=aligned_file1, aligned_file2=aligned_file2)

@app.route('/history')
def history():
    """View user's alignment history."""
    if not current_user():
        return redirect(url_for('login'))

    alignments = AlignmentHistory.query.filter_by(user_id=session['user_id']).order_by(AlignmentHistory.date_created.desc()).all()
    return render_template('based/history.html', alignments=alignments)

@app.route('/about')
def about():
    """About page."""
    if not current_user():
        return redirect(url_for('login'))
    return render_template('based/about.html')

if __name__ == '__main__':
    app.run(debug=True)
