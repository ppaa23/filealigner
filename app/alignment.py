import tokenize
from io import StringIO


def tokenize_code(code):
    """
    Tokenize Python code into raw tokens.
    :param code: Python code as a string.
    :return: List of tokens representing raw constructs.
    """
    tokens = []
    current_block = []
    try:
        for token in tokenize.generate_tokens(StringIO(code).readline):
            token_type = token.type
            token_string = token.string

            # Handle imports
            if token_type == tokenize.NAME and token_string in ("import", "from"):
                if current_block:
                    tokens.append(" ".join(current_block))
                    current_block = []
                current_block.append("import_statement")

            # Handle function definitions
            elif token_type == tokenize.NAME and token_string == "def":
                if current_block:
                    tokens.append(" ".join(current_block))
                    current_block = []
                current_block.append("function_def")

            # Handle class definitions
            elif token_type == tokenize.NAME and token_string == "class":
                if current_block:
                    tokens.append(" ".join(current_block))
                    current_block = []
                current_block.append("class_def")

            # Handle loops
            elif token_type == tokenize.NAME and token_string in ("for", "while"):
                if current_block:
                    tokens.append(" ".join(current_block))
                    current_block = []
                current_block.append("loop")

            # Handle conditionals
            elif token_type == tokenize.NAME and token_string in ("if", "elif", "else"):
                if current_block:
                    tokens.append(" ".join(current_block))
                    current_block = []
                current_block.append("conditional")

            # Handle docstrings
            elif token_type == tokenize.STRING:
                if current_block:
                    tokens.append(" ".join(current_block))
                    current_block = []
                current_block.append("docstring")

            # Ignore comments
            elif token_type == tokenize.COMMENT:
                continue

            # Handle indents and newlines
            elif token_type in (tokenize.INDENT, tokenize.DEDENT, tokenize.NEWLINE):
                if current_block:
                    tokens.append(" ".join(current_block))
                    current_block = []

            # Collect general tokens
            else:
                current_block.append(token_string)

        # Append the last block if it exists
        if current_block:
            tokens.append(" ".join(current_block))
    except tokenize.TokenError:
        pass
    return tokens

def abstract_tokens(tokens):
    """
    Abstract raw tokens into high-level constructs.
    :param tokens: List of raw tokens.
    :return: List of abstracted tokens.
    """
    abstracted_tokens = []
    for token in tokens:
        # Abstract specific constructs
        if "function_def" in token:
            abstracted_tokens.append("function_def")
        elif "class_def" in token:
            abstracted_tokens.append("class_def")
        elif "loop" in token:
            abstracted_tokens.append("loop")
        elif "conditional" in token:
            abstracted_tokens.append("conditional")
        elif "docstring" in token:
            abstracted_tokens.append("docstring")
        elif "import_statement" in token:
            abstracted_tokens.append("import_statement")
        else:
            # General abstraction for remaining tokens
            abstracted_tokens.append("general_token")
    return abstracted_tokens

def needleman_wunsch(seq1, seq2, match=2, mismatch=-1, gap=-2):
    """
    Perform Needleman-Wunsch alignment on two sequences.
    :param seq1: First sequence (list of tokens).
    :param seq2: Second sequence (list of tokens).
    :param match: Score for a match.
    :param mismatch: Penalty for a mismatch.
    :param gap: Penalty for a gap.
    :return: Alignment score and aligned sequences.
    """
    n, m = len(seq1), len(seq2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    # Initialize the scoring matrix
    for i in range(1, n + 1):
        dp[i][0] = dp[i - 1][0] + gap
    for j in range(1, m + 1):
        dp[0][j] = dp[0][j - 1] + gap

    # Fill the scoring matrix
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if seq1[i - 1] == seq2[j - 1]:
                score = match
            else:
                score = mismatch
            dp[i][j] = max(dp[i - 1][j - 1] + score, dp[i - 1][j] + gap, dp[i][j - 1] + gap)

    # Backtrack to get the aligned sequences
    aligned_seq1, aligned_seq2 = [], []
    i, j = n, m
    while i > 0 and j > 0:
        if seq1[i - 1] == seq2[j - 1]:
            aligned_seq1.append(seq1[i - 1])
            aligned_seq2.append(seq2[j - 1])
            i -= 1
            j -= 1
        elif dp[i][j] == dp[i - 1][j] + gap:
            aligned_seq1.append(seq1[i - 1])
            aligned_seq2.append("-")
            i -= 1
        else:
            aligned_seq1.append("-")
            aligned_seq2.append(seq2[j - 1])
            j -= 1

    while i > 0:
        aligned_seq1.append(seq1[i - 1])
        aligned_seq2.append("-")
        i -= 1
    while j > 0:
        aligned_seq1.append("-")
        aligned_seq2.append(seq2[j - 1])
        j -= 1

    aligned_seq1.reverse()
    aligned_seq2.reverse()
    return dp[n][m], aligned_seq1, aligned_seq2

def calculate_normalized_similarity(score, len_seq1, len_seq2):
    norm_similarity = score / max(len_seq1, len_seq2)
    return norm_similarity

def perform_alignment(file1_content, file2_content):
    """
    Perform pairwise alignment for Python files using token-based Needleman-Wunsch algorithm.
    Calculate E-value for the alignment score.
    :param file1_content: Content of the first Python file.
    :param file2_content: Content of the second Python file.
    :return: Dictionary with similarity score, aligned sequences, and E-value.
    """
    # Tokenize and abstract both files
    tokens1 = abstract_tokens(tokenize_code(file1_content))
    tokens2 = abstract_tokens(tokenize_code(file2_content))

    # Perform alignment
    alignment_score, aligned_tokens1, aligned_tokens2 = needleman_wunsch(tokens1, tokens2)

    # Calculate matches
    matches = sum(1 for t1, t2 in zip(aligned_tokens1, aligned_tokens2) if t1 == t2 and t1 != "-" and t2 != "-")
    total_length = len(aligned_tokens1)  # Includes gaps and mismatches

    # Calculate similarity as the ratio of matches to total alignment length
    similarity = matches / total_length if total_length > 0 else 0

    # Calculate normalized similarity
    norm_score = calculate_normalized_similarity(alignment_score, len(tokens1), len(tokens2))

    return {
        "similarity": round(similarity, 3),
        "needleman_score": alignment_score,
        "norm_score": round(norm_score, 3),
        "aligned_file1": " ".join(aligned_tokens1),
        "aligned_file2": " ".join(aligned_tokens2)
    }
