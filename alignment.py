
# GeneWeaver - DNA Sequence Alignment Engine

from validation import validate_dna


def needleman_wunsch(seq1, seq2, match=1, mismatch=-1, gap=-1):
    """Perform global DNA sequence alignment."""

    rows = len(seq1) + 1
    cols = len(seq2) + 1

    matrix = [[0 for _ in range(cols)] for _ in range(rows)]

    # Initialize first row and column
    for i in range(rows):
        matrix[i][0] = i * gap

    for j in range(cols):
        matrix[0][j] = j * gap

    # Fill scoring matrix
    for i in range(1, rows):
        for j in range(1, cols):
            score = match if seq1[i - 1] == seq2[j - 1] else mismatch

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
            score = match if seq1[i - 1] == seq2[j - 1] else mismatch

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


def smith_waterman(seq1, seq2, match=1, mismatch=-1, gap=-1):
    """Perform local DNA sequence alignment."""

    rows = len(seq1) + 1
    cols = len(seq2) + 1

    matrix = [[0 for _ in range(cols)] for _ in range(rows)]

    max_score = 0
    max_position = (0, 0)

    # Fill scoring matrix
    for i in range(1, rows):
        for j in range(1, cols):
            score = match if seq1[i - 1] == seq2[j - 1] else mismatch

            diagonal = matrix[i - 1][j - 1] + score
            up = matrix[i - 1][j] + gap
            left = matrix[i][j - 1] + gap

            matrix[i][j] = max(0, diagonal, up, left)

            if matrix[i][j] > max_score:
                max_score = matrix[i][j]
                max_position = (i, j)

    # Traceback from highest scoring position
    aligned1 = ""
    aligned2 = ""

    i, j = max_position

    while i > 0 and j > 0 and matrix[i][j] > 0:
        score = match if seq1[i - 1] == seq2[j - 1] else mismatch

        if matrix[i][j] == matrix[i - 1][j - 1] + score:
            aligned1 = seq1[i - 1] + aligned1
            aligned2 = seq2[j - 1] + aligned2
            i -= 1
            j -= 1

        elif matrix[i][j] == matrix[i - 1][j] + gap:
            aligned1 = seq1[i - 1] + aligned1
            aligned2 = "-" + aligned2
            i -= 1

        elif matrix[i][j] == matrix[i][j - 1] + gap:
            aligned1 = "-" + aligned1
            aligned2 = seq2[j - 1] + aligned2
            j -= 1

        else:
            break

    return aligned1, aligned2, max_score


def run_geneweaver():
    """Run GeneWeaver from the terminal."""

    print("\n===================================")
    print("       GENEWEAVER ENGINE")
    print("   DNA Sequence Alignment System")
    print("===================================")

    sequence1 = input("\nEnter first DNA sequence: ").strip()
    sequence2 = input("Enter second DNA sequence: ").strip()

    valid1 = validate_dna(sequence1)
    valid2 = validate_dna(sequence2)

    if not valid1 or not valid2:
        print("\nError: Invalid DNA sequence.")
        print("Only A, T, C and G are allowed.")
        return

    sequence1 = "".join(sequence1.split()).upper()
    sequence2 = "".join(sequence2.split()).upper()

    aligned1, aligned2, score = needleman_wunsch(sequence1, sequence2)

    print("\nAligned Sequence 1:", aligned1)
    print("Aligned Sequence 2:", aligned2)
    print("Alignment Score:", score)


if __name__ == "__main__":
    run_geneweaver()
