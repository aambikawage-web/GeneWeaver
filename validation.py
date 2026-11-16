
# GeneWeaver - DNA Sequence Validation

VALID_BASES = {"A", "T", "C", "G"}


def normalize_dna(sequence):
    """Convert DNA sequence to uppercase and remove whitespace."""

    if not isinstance(sequence, str):
        return ""

    return "".join(sequence.split()).upper()


def validate_dna_details(sequence):
    """Validate DNA and return detailed results."""

    if not isinstance(sequence, str):
        return False, "", "Input must be text."

    cleaned_sequence = normalize_dna(sequence)

    if not cleaned_sequence:
        return False, cleaned_sequence, "DNA sequence cannot be empty."

    invalid_bases = []

    for position, base in enumerate(cleaned_sequence, start=1):
        if base not in VALID_BASES:
            invalid_bases.append(f"{base} at position {position}")

    if invalid_bases:
        message = "Invalid characters: " + ", ".join(invalid_bases)
        return False, cleaned_sequence, message

    return True, cleaned_sequence, "Valid DNA sequence."


def validate_dna(sequence):
    """Return True if the DNA sequence is valid."""

    is_valid, _, _ = validate_dna_details(sequence)
    return is_valid


def get_dna_statistics(sequence):
    """Calculate DNA length and nucleotide counts."""

    is_valid, cleaned, message = validate_dna_details(sequence)

    if not is_valid:
        return {"valid": False, "message": message}

    length = len(cleaned)

    counts = {
        "A": cleaned.count("A"),
        "T": cleaned.count("T"),
        "C": cleaned.count("C"),
        "G": cleaned.count("G")
    }

    gc_content = ((counts["G"] + counts["C"]) / length) * 100

    return {
        "valid": True,
        "length": length,
        "counts": counts,
        "gc_content": round(gc_content, 2),
        "message": "DNA statistics calculated successfully."
    }
