def perform_alignment(file1_content, file2_content):
    """
    Perform pairwise alignment between two file contents.
    :param file1_content: Content of the first file as a string.
    :param file2_content: Content of the second file as a string.
    :return: Dictionary with similarity score and aligned contents.
    """
    # Normalize line endings to ensure consistency
    file1_content = file1_content.replace("\r\n", "\n").strip()
    file2_content = file2_content.replace("\r\n", "\n").strip()

    # Example alignment logic: character-by-character comparison
    matches = sum(1 for a, b in zip(file1_content, file2_content) if a == b)
    total = max(len(file1_content), len(file2_content))
    similarity = matches / total if total > 0 else 0

    return {
        "similarity": round(similarity, 2),
        "aligned_file1": file1_content,
        "aligned_file2": file2_content,
    }
