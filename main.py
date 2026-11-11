def align_sequences(seq1, seq2):
    matches = 0
    mismatches = 0

    for i in range(min(len(seq1), len(seq2))):
        if seq1[i] == seq2[i]:
            matches += 1
        else:
            mismatches += 1

    print("\nGeneWeaver DNA Comparison")
    print("-------------------------")
    print("Sequence 1:", seq1)
    print("Sequence 2:", seq2)
    print("Matching positions:", matches)
    print("Different positions:", mismatches)


sequence1 = "ATCGATCG"
sequence2 = "ATCGTTCG"

align_sequences(sequence1, sequence2)
