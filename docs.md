# Application Documentation

## List of Endpoints

### `/` (GET)
- **Description**: Displays the homepage with a welcome message or relevant app information.
- **Shows**: Introduction to the app, any links to navigate to other pages.
- **Actions**: None.
- **Elements**: Links to other features of the app.

---

### `/alignments/create` (GET)
- **Description**: Displays a form where the user can upload files for alignment.
- **Shows**: A form to upload two files for alignment.
- **Actions**: Allows users to upload files.
- **Elements**:
  - File upload input for the first file.
  - File upload input for the second file.
  - A submit button labeled "Align Files."

### `/alignments/create` (POST)
- **Description**: Processes the uploaded files and performs alignment.
- **Shows**: Results of the alignment, including any visualizations or downloadable results.
- **Actions**: Allows the user to download the alignment output.
- **Elements**:
  - Download button for the alignment result.
  - A "Back" button to return to the upload page.

---

### `/alignments/view/<alignment_id>` (GET)
- **Description**: Displays a specific alignment result by its unique ID.
- **Shows**: Details of the selected alignment, including a preview and any metadata.
- **Actions**: Allows the user to analyze or download the alignment.
- **Elements**:
  - A download button for the alignment result.
  - Any additional options for analysis (if applicable).

---

### `/history` (GET)
- **Description**: Shows a history of previously processed alignments.
- **Shows**: A list of all previously created alignments with their IDs, timestamps, and statuses.
- **Actions**: Allows the user to view or delete specific alignments.
- **Elements**:
  - A "View" button for each alignment.
  - A "Delete" button for each alignment.

---

### `/about` (GET)
- **Description**: Displays information about the app and its functionality.
- **Shows**: Static information about the purpose and use of the app.
- **Actions**: None.
- **Elements**: None.
