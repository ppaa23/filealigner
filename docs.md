# Application Documentation

## List of Endpoints

---

### `/` (GET)
- **Description**: Displays the homepage with a welcome message and navigation options.
- **Shows**: Introduction to the app and links to other features.
- **Actions**: None.
- **Elements**:
  - Links to single file alignment, multiple file alignment, history, and file similarity search pages.

---

### `/alignments/create` (GET)
- **Description**: Displays a form where users can upload two files for alignment.
- **Shows**: A form to upload two files.
- **Actions**: Allows users to upload files for alignment.
- **Elements**:
  - File upload input for the first file.
  - File upload input for the second file.
  - A submit button labeled "Align Files."

---

### `/alignments/create` (POST)
- **Description**: Processes the uploaded files and generates a single alignment.
- **Shows**: The alignment results, including any visualizations or downloadable results.
- **Actions**: Allows the user to download the alignment output.
- **Elements**:
  - Download button for the alignment result.
  - A "Back" button to return to the upload page.

---

### `/alignments/multiple` (GET)
- **Description**: Displays a form where users can upload multiple files for alignment.
- **Shows**: A form to upload multiple files.
- **Actions**: Allows users to upload files for a multiple alignment.
- **Elements**:
  - File upload input that accepts multiple files.
  - A submit button labeled "Generate Alignment and Tree."

---

### `/alignments/multiple` (POST)
- **Description**: Processes the uploaded files, generates a multiple alignment, and creates a phylogenetic tree.
- **Shows**: 
  - The results of the multiple alignment.
  - A visualization of the phylogenetic tree.
- **Actions**: 
  - Allows the user to download the multiple alignment output.
  - Displays a tree visualization.
- **Elements**:
  - Download button for the multiple alignment result.
  - A tree visualization section.

---

### `/search` (GET)
- **Description**: Displays a form for uploading a query file to find the most similar file in the database.
- **Shows**: A form to upload a single query file.
- **Actions**: Allows users to submit a file for similarity search.
- **Elements**:
  - File upload input for the query file.
  - A submit button labeled "Search."

---

### `/search` (POST)
- **Description**: Processes the query file, performs a heuristic search, and displays the most similar file from the database.
- **Shows**:
  - The name and metadata of the most similar file.
  - The similarity score.
- **Actions**: Allows users to view the most similar file.
- **Elements**:
  - Display of the matched file.
  - A "Back" button to return to the search page.

---

### `/alignments/view/<alignment_id>` (GET)
- **Description**: Displays the details of a specific alignment by its unique ID.
- **Shows**: 
  - Details of the selected alignment.
  - Any metadata or preview of the result.
- **Actions**: Allows the user to analyze or download the alignment.
- **Elements**:
  - A download button for the alignment result.
  - Metadata and preview section.

---

### `/history` (GET)
- **Description**: Displays a history of all previously processed alignments and uploaded files.
- **Shows**: 
  - A list of all alignments with their IDs, timestamps, and statuses.
  - Uploaded files with details like name, size, and timestamp.
- **Actions**:
  - Allows the user to view, download, or delete specific alignments or files.
- **Elements**:
  - A "View" button for each alignment.
  - A "Delete" button for each alignment or file.

---

### `/about` (GET)
- **Description**: Displays static information about the app and its functionality.
- **Shows**: Details about the purpose and use of the app.
- **Actions**: None.
- **Elements**: None.

---

## Summary of Features

- **Single File Alignment**: Upload two files and generate an alignment.
- **Multiple File Alignment**: Upload multiple files and generate a combined alignment along with a phylogenetic tree.
- **Alignment Visualization**: View and download alignment results.
- **Phylogenetic Tree Display**: Visualize the tree structure created from multiple alignments.
- **File Similarity Search**: Use heuristic search to find the most similar file from the database of previously uploaded files.
- **History Management**: View, manage, and delete previously created alignments and uploaded files.
