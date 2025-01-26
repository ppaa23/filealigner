import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from alignment import perform_alignment, tokenize_code

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

def manage_alignment_storage(user_id):
    """Ensure only the last 5 alignments have files saved on disk."""
    alignments = AlignmentHistory.query.filter_by(user_id=user_id).order_by(AlignmentHistory.date_created).all()
    if len(alignments) > 5:
        for alignment in alignments[:-5]:  # Keep only the last 5 alignments
            alignment_dir = os.path.join("uploads", str(user_id), alignment.alignment_id)
            if os.path.exists(alignment_dir):
                for file in os.listdir(alignment_dir):
                    os.remove(os.path.join(alignment_dir, file))
                os.rmdir(alignment_dir)

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

@app.route('/tools/pairwise', methods=['GET', 'POST'])
def align():
    """Handle pairwise alignment for Python files."""
    if not current_user():
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Get files from the request
        file1 = request.files.get('file1')
        file2 = request.files.get('file2')

        # Initialize an error list
        errors = []

        # Check if files are uploaded
        if not file1 or file1.filename == '':
            errors.append("File 1 is missing.")
        if not file2 or file2.filename == '':
            errors.append("File 2 is missing.")

        # Check file extensions
        if file1 and not file1.filename.endswith('.py'):
            errors.append("File 1 must be a Python file with a .py extension.")
        if file2 and not file2.filename.endswith('.py'):
            errors.append("File 2 must be a Python file with a .py extension.")

        # Check file sizes
        max_size = 1 * 1024 * 1024  # 1MB in bytes
        if file1 and file1.content_length > max_size:
            errors.append("File 1 must be smaller than 1MB.")
        if file2 and file2.content_length > max_size:
            errors.append("File 2 must be smaller than 1MB.")

        # If errors exist, flash them and return to the page
        if errors:
            for error in errors:
                flash(error, "error")
            return redirect(url_for('align'))

        # Read and process file content
        file1_content = file1.read().decode('utf-8', errors='replace')
        file2_content = file2.read().decode('utf-8', errors='replace')
        alignment_result = perform_alignment(file1_content, file2_content)

        # Save files and alignment history
        alignment_id = str(uuid.uuid4())
        user_dir = os.path.join("uploads", str(session['user_id']))
        alignment_dir = os.path.join(user_dir, alignment_id)
        os.makedirs(alignment_dir, exist_ok=True)

        file1_path = os.path.join(alignment_dir, "file1.py")
        file2_path = os.path.join(alignment_dir, "file2.py")

        with open(file1_path, "w", encoding="utf-8") as f1, open(file2_path, "w", encoding="utf-8") as f2:
            f1.write(file1_content)
            f2.write(file2_content)

        alignment = AlignmentHistory(
            user_id=session['user_id'],
            file1_name=file1.filename,
            file2_name=file2.filename,
            similarity=alignment_result['similarity'],
            alignment_id=alignment_id
        )
        db.session.add(alignment)
        db.session.commit()

        # Manage storage for older alignments
        manage_alignment_storage(session['user_id'])

        # Redirect to results page
        return redirect(url_for('alignment_results', alignment_id=alignment_id))

    return render_template('based/align.html')


@app.route('/results/p/<alignment_id>')
def alignment_results(alignment_id):
    """Display the results of a specific alignment."""
    if not current_user():
        return redirect(url_for('login'))

    alignment = AlignmentHistory.query.filter_by(alignment_id=alignment_id, user_id=session['user_id']).first()
    if not alignment:
        flash("Result not found.", "error")
        return redirect(url_for('history'))

    user_dir = os.path.join("uploads", str(session['user_id']))
    alignment_dir = os.path.join(user_dir, alignment_id)

    file1_path = os.path.join(alignment_dir, "file1.py")
    file2_path = os.path.join(alignment_dir, "file2.py")

    try:
        with open(file1_path, "r", encoding="utf-8") as f1, open(file2_path, "r", encoding="utf-8") as f2:
            file1_content = "\n".join(line.strip() for line in f1 if line.strip())
            file2_content = "\n".join(line.strip() for line in f2 if line.strip())
    except FileNotFoundError:
        flash("One or both files are missing for this alignment.", "error")
        return redirect(url_for('history'))

    file1_tokens = tokenize_code(file1_content)
    file2_tokens = tokenize_code(file2_content)

    return render_template('based/results.html',
                           similarity=alignment.similarity,
                           file1=file1_content,
                           file2=file2_content,
                           file1_tokens=file1_tokens,
                           file2_tokens=file2_tokens,
                           file1_name=alignment.file1_name,
                           file2_name=alignment.file2_name)

@app.route('/tools/multialign', methods=['GET', 'POST'])
def multialign():
    """Handle multiple alignment page."""
    if not current_user():
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Retrieve uploaded files
        files = request.files.getlist('files')

        # Validate the number of files
        if len(files) < 2:
            flash("Please upload at least two files for multiple alignment.", "error")
            return redirect(url_for('multialign'))

        # Placeholder for multiple alignment logic
        flash("Multiple alignment performed successfully!", "success")
        return redirect(url_for('history'))

    return render_template('based/multialign.html')

@app.route('/history')
def history():
    """View user's alignment history."""
    if not current_user():
        return redirect(url_for('login'))

    alignments = AlignmentHistory.query.filter_by(user_id=session['user_id']).order_by(AlignmentHistory.date_created.desc()).all()
    recent_alignment_ids = [alignment.alignment_id for alignment in alignments[:5]]

    return render_template('based/history.html', alignments=alignments, recent_alignment_ids=recent_alignment_ids)

@app.route('/about')
def about():
    """About page."""
    if not current_user():
        return redirect(url_for('login'))
    return render_template('based/about.html')

if __name__ == '__main__':
    app.run(debug=True)
