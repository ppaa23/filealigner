#import os
import uuid
import logging
from logging.handlers import RotatingFileHandler
from flasgger import Swagger
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from .alignment import perform_alignment

app = Flask(__name__)
app.secret_key = "23"

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
    file1_content = db.Column(db.Text, nullable=False)  # Content of File 1
    file2_content = db.Column(db.Text, nullable=False)  # Content of File 2
    aligned_file1 = db.Column(db.Text, nullable=False)  # Aligned content of File 1
    aligned_file2 = db.Column(db.Text, nullable=False)  # Aligned content of File 2
    score = db.Column(db.Float, nullable=False)
    similarity = db.Column(db.Float, nullable=False)
    norm_score = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    alignment_id = db.Column(db.String(36), unique=True, nullable=False)


with app.app_context():
    db.create_all()

class SingletonLogger:
    """Singleton Logger for application-wide logging."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SingletonLogger, cls).__new__(cls)
            cls._instance.logger = logging.getLogger("FlaskAppLogger")
            cls._instance.logger.setLevel(logging.INFO)

            handler = RotatingFileHandler('app.log', maxBytes=5 * 1024 * 1024, backupCount=3)
            handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            cls._instance.logger.addHandler(handler)

        return cls._instance

    @staticmethod
    def get_logger():
        """Return the singleton logger instance."""
        return SingletonLogger()._instance.logger

# Initialize the logger
app.logger = SingletonLogger.get_logger()

swagger = Swagger(app)

def current_user():
    """Retrieve the currently logged-in user."""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

"""
def manage_alignment_storage(user_id):
    alignments = AlignmentHistory.query.filter_by(user_id=user_id).order_by(AlignmentHistory.date_created).all()
    if len(alignments) > 5:
        for alignment in alignments[:-5]:  # Keep only the last 5 alignments
            alignment_dir = os.path.join("uploads", str(user_id), alignment.alignment_id)
            if os.path.exists(alignment_dir):
                for file in os.listdir(alignment_dir):
                    os.remove(os.path.join(alignment_dir, file))
                os.rmdir(alignment_dir)
"""

@app.route('/')
def index():
    """
    Landing page.
    ---
    tags:
      - Pages
    responses:
      200:
        description: Displays the landing page or redirects to /home if the user is logged in.
    """
    app.logger.info("Index page accessed.")
    if current_user():
        return redirect(url_for('home'), code=303)
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register a new user.
    ---
    tags:
      - Authentication
    parameters:
      - name: username
        in: formData
        type: string
        required: true
        description: The desired username
      - name: password
        in: formData
        type: string
        required: true
        description: The user's password
      - name: confirm_password
        in: formData
        type: string
        required: true
        description: Confirm the user's password
    responses:
      200:
        description: Successful registration and redirection to /home
      400:
        description: Registration error (e.g., passwords do not match)
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            app.logger.warning("Registration failed: Passwords do not match.")
            flash('Passwords do not match.', 'error')
            return render_template('register.html'), 400

        if User.query.filter_by(username=username).first():
            app.logger.warning("Registration failed: Username already exists.")
            flash("Username already exists. Please choose another one.", "error")
            return render_template('register.html'), 400

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        app.logger.info(f"User registered successfully: {username}")
        return redirect(url_for('home'), code=303)

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login.
    ---
    tags:
      - Auth
    parameters:
      - name: username
        in: formData
        type: string
        required: true
        description: Username of the user
      - name: password
        in: formData
        type: string
        required: true
        description: Password of the user
    responses:
      200:
        description: Login successful
      401:
        description: Invalid username or password
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            app.logger.info(f"User authorized successfully: {username}")
            session['user_id'] = user.id
            return redirect(url_for('home'), code=303)
        else:
            app.logger.warning(f"Authorization failed: Invalid username or password: { user }")
            flash("Invalid username or password.", "error")
            return render_template('login.html'), 401

    return render_template('login.html', code=303)

@app.route('/logout')
def logout():
    """
    Log out the current user.
    ---
    tags:
      - Authentication
    responses:
      200:
        description: The user is successfully logged out.
    """
    user=current_user()
    app.logger.info(f"User signed out successfully: { user }")
    session.pop('user_id', None)
    return redirect(url_for('index'), code=303)

@app.route('/home')
def home():
    """
    Home page for logged-in users.
    ---
    tags:
      - Pages
    responses:
      200:
        description: Displays the home page for logged-in users.
      302:
        description: Redirects to the login page if the user is not authenticated.
    """
    if not current_user():
        return {"error": "Unauthorized. Please log in."}, 401
    return render_template('based/home.html', current_user=current_user())

@app.route('/tools/pairwise', methods=['GET', 'POST'])
def align():
    """
    Perform pairwise alignment for Python files.
    ---
    tags:
      - Tools
    consumes:
      - multipart/form-data
    parameters:
      - name: file1
        in: formData
        type: file
        required: true
        description: First Python file to be compared
      - name: file2
        in: formData
        type: file
        required: true
        description: Second Python file to be compared
    responses:
      200:
        description: Alignment completed successfully
      400:
        description: Error due to missing or invalid files
    """
    if not current_user():
        return {"error": "Unauthorized. Please log in."}, 401

    if request.method == 'POST':
        # Retrieve uploaded files
        file1 = request.files.get('file1')
        file2 = request.files.get('file2')

        # Initialize an error list
        errors = []

        # Validate file uploads
        if not file1 or not file2:
            app.logger.warning("Alignment failed: Not all files uploaded.")
            errors.append("Both files are required.")
        if file1 and not file1.filename.endswith('.py'):
            app.logger.warning("Alignment failed: Uploaded not a .py file.")
            errors.append("File 1 must be a Python file with a .py extension.")
        if file2 and not file2.filename.endswith('.py'):
            app.logger.warning("Alignment failed: Uploaded not a .py file.")
            errors.append("File 2 must be a Python file with a .py extension.")

        # Validate file sizes
        max_size = 1 * 1024 * 1024  # 1MB in bytes
        if file1 and file1.content_length > max_size:
            app.logger.warning("Alignment failed: Uploaded too big file.")
            errors.append("File 1 must be smaller than 1MB.")
        if file2 and file2.content_length > max_size:
            app.logger.warning("Alignment failed: Uploaded too big file.")
            errors.append("File 2 must be smaller than 1MB.")

        # Handle errors
        if errors:
            for error in errors:
                flash(error, "error")
            return redirect(url_for('align'), code=303)

        # Read file content
        file1_content = file1.read().decode('utf-8', errors='replace').strip()
        file2_content = file2.read().decode('utf-8', errors='replace').strip()

        # Perform alignment
        alignment_result = perform_alignment(file1_content, file2_content)

        # Save results to the database
        alignment = AlignmentHistory(
            user_id=session['user_id'],
            file1_name=file1.filename,
            file2_name=file2.filename,
            file1_content=file1_content,
            file2_content=file2_content,
            aligned_file1=alignment_result['aligned_file1'],
            aligned_file2=alignment_result['aligned_file2'],
            score=alignment_result['needleman_score'],
            similarity=alignment_result['similarity'],
            norm_score=alignment_result['norm_score'],
            alignment_id=str(uuid.uuid4())
        )
        db.session.add(alignment)
        db.session.commit()


        app.logger.info(f"Alignment performed successfully: { AlignmentHistory.alignment_id }")

        return redirect(url_for('alignment_results', alignment_id=alignment.alignment_id), code=303)

    return render_template('based/align.html')

@app.route('/results/p/<alignment_id>')
def alignment_results(alignment_id):
    """
    Retrieve and display the results of a specific alignment.
    ---
    tags:
      - Results
    parameters:
      - name: alignment_id
        in: path
        type: string
        required: true
        description: The unique ID of the alignment result
    responses:
      200:
        description: Displays the alignment results
      404:
        description: Alignment result not found
    """
    if not current_user():
        return {"error": "Unauthorized. Please log in."}, 401

    alignment = AlignmentHistory.query.filter_by(
        alignment_id=alignment_id, user_id=session['user_id']
    ).first()

    if not alignment:
        app.logger.warning("Alignment displaying failed: Result not found or access denied.")
        return {"error": "Alignment result not found."}, 404

    # Render results with alignment data from the database
    return render_template(
        'based/results.html',
        score=alignment.score,
        similarity=alignment.similarity,
        norm_score=alignment.norm_score,
        file1=alignment.file1_content,
        file2=alignment.file2_content,
        file1_tokens=alignment.aligned_file1.split("\n"),  # Split tokens by lines
        file2_tokens=alignment.aligned_file2.split("\n"),  # Split tokens by lines
        file1_name=alignment.file1_name,
        file2_name=alignment.file2_name
    ), 200

@app.route('/history')
def history():
    """
    View user's alignment history.
    ---
    tags:
      - History
    responses:
      200:
        description: Displays a list of past alignment results for the logged-in user.
      302:
        description: Redirects to login page if the user is not authenticated.
    """
    if not current_user():
        return {"error": "Unauthorized. Please log in."}, 401

    alignments = AlignmentHistory.query.filter_by(user_id=session['user_id']).order_by(
        AlignmentHistory.date_created.desc()
    ).all()

    return render_template('based/history.html', alignments=alignments), 200

if __name__ == '__main__':
    app.run(debug=True)
