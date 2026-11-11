
# GeneWeaver - DNA Sequence Alignment Engine

from validation import validate_dna


def needleman_wunsch(seq1, seq2):
    match = 1
    mismatch = -1
    gap = -1

    rows = len(seq1) + 1
    cols = len(seq2) + 1

    # Create scoring matrix
    matrix = [[0 for _ in range(cols)] for _ in range(rows)]

    # Initialize first row and column
    for i in range(rows):
        matrix[i][0] = i * gap

    for j in range(cols):
        matrix[0][j] = j * gap

    # Fill scoring matrix
    for i in range(1, rows):
        for j in range(1, cols):

            if seq1[i - 1] == seq2[j - 1]:
                score = match
            else:
                score = mismatch

            diagonal = matrix[i - 1][j - 1] + score
            up = matrix[i - 1][j] + gap
            left = matrix[i][j - 1] + gap

            matrix[i][j] = max(diagonal, up, left)

    # Traceback
    aligned1 = ""
    aligned2 = ""

    i = len(seq1)
    j = len(seq2)

    while i > 0 or j > 0:

        if i > 0 and j > 0:
            if seq1[i - 1] == seq2[j - 1]:
                score = match
            else:
                score = mismatch

            if matrix[i][j] == matrix[i - 1][j - 1] + score:
                aligned1 = seq1[i - 1] + aligned1
                aligned2 = seq2[j - 1] + aligned2
                i -= 1
                j -= 1
                continue

        if i > 0 and matrix[i][j] == matrix[i - 1][j] + gap:
            aligned1 = seq1[i - 1] + aligned1
            aligned2 = "-" + aligned2
            i -= 1

        else:
            aligned1 = "-" + aligned1
            aligned2 = seq2[j - 1] + aligned2
            j -= 1

    return aligned1, aligned2, matrix[-1][-1]


def run_geneweaver():

    print("\n===================================")
    print("       GENEWEAVER ENGINE")
    print("   DNA Sequence Alignment System")
    print("===================================")

    sequence1 = input("\nEnter first DNA sequence: ").strip().upper()
    sequence2 = input("Enter second DNA sequence: ").strip().upper()

    # Validate DNA sequences
    if not validate_dna(sequence1) or not validate_dna(sequence2):
        print("\nError: Invalid DNA sequence.")
        print("Only A, T, C and G are allowed.")
        return

    print("\nBoth DNA sequences are valid.")

    # Perform alignment
    result1, result2, score = needleman_wunsch(sequence1, sequence2)

    print("\n========== ALIGNMENT RESULTS ==========")
    print("Original Sequence 1:", sequence1)
    print("Original Sequence 2:", sequence2)
    print("Aligned Sequence 1: ", result1)
    print("Aligned Sequence 2: ", result2)
    print("Alignment Score:    ", score)

    # Calculate matching positions
    matches = sum(
        a == b and a != "-"
        for a, b in zip(result1, result2)
    )

    print("Matching positions:", matches)
    print("Different positions:", len(result1) - matches)
    print("=======================================")


if __name__ == "__main__":
    run_geneweaver()
