[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/A0dLY9j1)

# GoGiAlign

## Description
This is a Flask-based web application that provides tools for creating file alignments. The app supports pairwise alignments, maintains an alignment history, and allows users to manage their alignment results.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/nup-csai/flask-project-ppaa23.git
   cd your-repo
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   flask run
   ```
or open the link below:
   ```bash
   https://flask-project-ppaa23-production.up.railway.app/
   ```

## Requirements
- Flask
- Flask-SQLAlchemy
- pytest
- requests
- flasgger
- Docker

## Features
- **User Registration & Authentication**: Users can register, log in, and log out.
- **Pairwise File Alignment**: Users can upload two Python files for comparison. Alignment is conducted using tokenization the given code and following application of Needleman-Wunsch algorithm (allowing to compare sequences with different coefficients for matches, mismatches and gaps). The result of the alignment is provided in the form of *similarity* (the part of matches), *score* (the maximum possible score for given coefficients) and *normalized score* (normalization for the maximum length of token sequence).
- **Alignment History**: Users can view past alignment results with timestamps.

## API Endpoints
- `/` (GET) - Displays the landing page.
- `/register` (GET, POST) - Handles user registration.
- `/login` (GET, POST) - Handles user authentication.
- `/logout` (GET) - Logs out the current user.
- `/home` (GET) - Displays the home page for logged-in users.
- `/tools/pairwise` (GET, POST) - Allows users to upload two Python files for alignment.
- `/results/p/<alignment_id>` (GET) - Displays the results of a specific alignment.
- `/history` (GET) - Displays the history of past alignments.

## Git
Development is managed through the `master` branch.

## Success Criteria
- Program successfully aligns given files, saves the result to history, and visualizes alignments.
- User authentication and session management work as expected.

## Video
Here is the video capture showing basic functionality and features of GoGiAlign: https://youtu.be/c2bIPEo1qEw
