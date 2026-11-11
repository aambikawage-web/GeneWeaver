# GeneWeaver - DNA Sequence Validation

def validate_dna(sequence):
    valid_bases = {"A", "T", "C", "G"}

    sequence = sequence.upper()

    if not sequence:
        return False

    return all(base in valid_bases for base in sequence)
