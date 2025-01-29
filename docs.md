# API Documentation

## List of Endpoints

---

### `/` (GET)
- **Description**: Displays the landing page with navigation options.
- **Response**: Renders the homepage.
- **Authentication**: Not required.

---

### `/register` (GET, POST)
- **Description**: Handles user registration.
- **GET**: Displays the registration form.
- **POST**: Processes user registration.
- **Request Parameters (form-data)**:
  - `username` (string, required)
  - `password` (string, required)
  - `confirm_password` (string, required)
- **Response**:
  - `200 OK`: Successful registration.
  - `400 Bad Request`: Registration failed (e.g., passwords do not match, username exists).
- **Authentication**: Not required.

---

### `/login` (GET, POST)
- **Description**: Handles user authentication.
- **GET**: Displays the login form.
- **POST**: Processes login.
- **Request Parameters (form-data)**:
  - `username` (string, required)
  - `password` (string, required)
- **Response**:
  - `200 OK`: Successful login.
  - `401 Unauthorized`: Invalid credentials.
- **Authentication**: Not required.

---

### `/logout` (GET)
- **Description**: Logs out the current user.
- **Response**:
  - Redirects to the landing page.
- **Authentication**: Required.

---

### `/home` (GET)
- **Description**: Displays the home page for logged-in users.
- **Response**:
  - `200 OK`: Renders the home page.
  - `401 Unauthorized`: User is not logged in.
- **Authentication**: Required.

---

### `/tools/pairwise` (GET, POST)
- **Description**: Allows users to upload two Python files for alignment.
- **GET**: Displays the file upload form.
- **POST**: Processes the uploaded files and performs pairwise alignment.
- **Request Parameters (multipart/form-data)**:
  - `file1` (file, required)
  - `file2` (file, required)
- **Response**:
  - `200 OK`: Successful alignment.
  - `400 Bad Request`: Missing or invalid files.
- **Authentication**: Required.

---

### `/results/p/<alignment_id>` (GET)
- **Description**: Displays the results of a specific alignment.
- **URL Parameters**:
  - `alignment_id` (string, required): Unique identifier for the alignment.
- **Response**:
  - `200 OK`: Displays alignment results.
  - `404 Not Found`: Alignment not found.
- **Authentication**: Required.

---

### `/history` (GET)
- **Description**: Displays the history of past alignments.
- **Response**:
  - `200 OK`: Renders the history page with a list of past alignments.
  - `401 Unauthorized`: User is not logged in.
- **Authentication**: Required.

---

## Summary of Features

- **User Registration & Authentication**: Allows users to register, log in, and log out.
- **Pairwise File Alignment**: Users can upload two Python files for comparison.
- **Alignment History**: Users can view past alignment results.