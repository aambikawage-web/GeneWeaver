
import streamlit as st
import time

from alignment import needleman_wunsch, smith_waterman
from validation import validate_dna_details, get_dna_statistics


# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="GeneWeaver",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 GeneWeaver")
st.subheader("GPU-Accelerated CRISPR Alignment Engine")
st.write("DNA Sequence Comparison and Alignment Dashboard")

st.divider()


# ---------------- FASTA FILE READER ----------------

def read_fasta(uploaded_file):
    """Read DNA sequences from a FASTA or text file."""

    content = uploaded_file.getvalue().decode("utf-8")
    sequences = []
    current_sequence = ""

    for line in content.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith(">"):
            if current_sequence:
                sequences.append(current_sequence)
                current_sequence = ""
        else:
            current_sequence += line

    if current_sequence:
        sequences.append(current_sequence)

    return sequences


# ---------------- DNA INPUT ----------------

st.header("DNA Sequence Input")

input_method = st.radio(
    "Choose input method",
    ["Manual Input", "Upload FASTA File"],
    horizontal=True
)

sequence1 = ""
sequence2 = ""

if input_method == "Upload FASTA File":

    uploaded_file = st.file_uploader(
        "Upload a FASTA file",
        type=["fasta", "fa", "txt"]
    )

    if uploaded_file is not None:

        try:
            sequences = read_fasta(uploaded_file)

            if len(sequences) < 2:
                st.error(
                    "Please upload a file containing at least two DNA sequences."
                )

            else:
                sequence1 = sequences[0]
                sequence2 = sequences[1]

                st.success("FASTA file uploaded successfully!")

                st.write("**First sequence:**")
                st.code(sequence1)

                st.write("**Second sequence:**")
                st.code(sequence2)

                if len(sequences) > 2:
                    st.info(
                        f"{len(sequences)} sequences found. "
                        "The first two sequences will be compared."
                    )

        except (UnicodeDecodeError, ValueError):
            st.error(
                "Unable to read the file. "
                "Please upload a valid text-based FASTA file."
            )

else:

    col1, col2 = st.columns(2)

    with col1:
        sequence1 = st.text_area(
            "Enter First DNA Sequence",
            value="ATCGATCG",
            height=120
        )

    with col2:
        sequence2 = st.text_area(
            "Enter Second DNA Sequence",
            value="ATCGTTCG",
            height=120
        )


# ---------------- DNA STATISTICS ----------------

if sequence1 and sequence2:

    with st.expander("View DNA Sequence Statistics"):

        stats1 = get_dna_statistics(sequence1)
        stats2 = get_dna_statistics(sequence2)

        if stats1["valid"] and stats2["valid"]:

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Sequence 1")
                st.write("Length:", stats1["length"])
                st.write("Nucleotide counts:", stats1["counts"])
                st.write("GC Content:", f'{stats1["gc_content"]}%')

            with col2:
                st.subheader("Sequence 2")
                st.write("Length:", stats2["length"])
                st.write("Nucleotide counts:", stats2["counts"])
                st.write("GC Content:", f'{stats2["gc_content"]}%')


# ---------------- ALIGNMENT CONFIGURATION ----------------

st.divider()
st.header("Alignment Configuration")

col1, col2, col3, col4 = st.columns(4)

with col1:
    algorithm = st.selectbox(
        "Choose Algorithm",
        ["Needleman-Wunsch (Global)", "Smith-Waterman (Local)"]
    )

with col2:
    match_score = st.number_input(
        "Match Score",
        min_value=1,
        value=1,
        step=1
    )

with col3:
    mismatch_score = st.number_input(
        "Mismatch Penalty",
        max_value=0,
        value=-1,
        step=1
    )

with col4:
    gap_penalty = st.number_input(
        "Gap Penalty",
        max_value=0,
        value=-1,
        step=1
    )


# ---------------- RUN ALIGNMENT ----------------

if st.button("🚀 Run DNA Alignment", type="primary"):

    if not sequence1 or not sequence2:

        st.error("Please enter or upload two DNA sequences.")

    else:

        valid1, cleaned1, message1 = validate_dna_details(sequence1)
        valid2, cleaned2, message2 = validate_dna_details(sequence2)

        if not valid1:
            st.error("Sequence 1: " + message1)

        if not valid2:
            st.error("Sequence 2: " + message2)

        if valid1 and valid2:

            st.success("Both DNA sequences are valid!")

            # Run selected alignment algorithm

            start_time = time.perf_counter()

            if algorithm == "Needleman-Wunsch (Global)":

                aligned1, aligned2, score = needleman_wunsch(
                    cleaned1,
                    cleaned2,
                    match=match_score,
                    mismatch=mismatch_score,
                    gap=gap_penalty
                )

            else:

                aligned1, aligned2, score = smith_waterman(
                    cleaned1,
                    cleaned2,
                    match=match_score,
                    mismatch=mismatch_score,
                    gap=gap_penalty
                )

            end_time = time.perf_counter()

            execution_time = (end_time - start_time) * 1000

            # ---------------- ALIGNMENT STATISTICS ----------------

            matches = sum(
                a == b and a != "-"
                for a, b in zip(aligned1, aligned2)
            )

            mismatches = sum(
                a != b and a != "-" and b != "-"
                for a, b in zip(aligned1, aligned2)
            )

            gaps = sum(
                a == "-" or b == "-"
                for a, b in zip(aligned1, aligned2)
            )

            alignment_length = len(aligned1)

            identity = (
                matches / alignment_length * 100
                if alignment_length > 0 else 0
            )

            # ---------------- DISPLAY RESULTS ----------------

            st.divider()
            st.header("Alignment Results")

            result1, result2, result3, result4 = st.columns(4)

            result1.metric("Alignment Score", score)
            result2.metric("Matches", matches)
            result3.metric("Mismatches", mismatches)
            result4.metric("Gap Columns", gaps)

            col1, col2 = st.columns(2)

            col1.metric(
                "Sequence Identity",
                f"{identity:.2f}%"
            )

            col2.metric(
                "Execution Time",
                f"{execution_time:.4f} ms"
            )

            # ---------------- COLOUR-CODED ALIGNMENT ----------------

            st.subheader("Aligned DNA Sequences")

            colored1 = ""
            colored2 = ""

            for a, b in zip(aligned1, aligned2):

                if a == "-" or b == "-":
                    color = "#D69E00"

                elif a == b:
                    color = "#16A34A"

                else:
                    color = "#DC2626"

                colored1 += (
                    f'<span style="color:{color};font-weight:bold;">{a}</span>'
                )

                colored2 += (
                    f'<span style="color:{color};font-weight:bold;">{b}</span>'
                )

            st.markdown(
                f"""
                <div style="
                    background-color: #222;
                    padding: 18px;
                    border-radius: 10px;
                    font-family: monospace;
                    font-size: 18px;
                    overflow-x: auto;
                    white-space: nowrap;
                ">
                    <div>Sequence 1: {colored1}</div>
                    <div>Sequence 2: {colored2}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # ---------------- COLOUR LEGEND ----------------

            st.write("**Colour Legend:**")

            st.markdown(
                """
                🟢 Green – Matching bases

                🔴 Red – Mismatching bases

                🟡 Yellow – Gaps
                """
            )

            st.success("DNA alignment completed successfully!")

            # ---------------- DOWNLOAD REPORT ----------------

            report = f"""
GENEWEAVER - DNA ALIGNMENT REPORT
=================================

Algorithm: {algorithm}

Original Sequence 1: {cleaned1}
Original Sequence 2: {cleaned2}

Aligned Sequence 1: {aligned1}
Aligned Sequence 2: {aligned2}

Scoring Configuration:
Match Score: {match_score}
Mismatch Penalty: {mismatch_score}
Gap Penalty: {gap_penalty}

Alignment Results:
Alignment Score: {score}
Matches: {matches}
Mismatches: {mismatches}
Gap Columns: {gaps}
Sequence Identity: {identity:.2f}%
Execution Time: {execution_time:.4f} ms

=================================
Generated by GeneWeaver
"""

            st.download_button(
                label="📥 Download Alignment Report",
                data=report,
                file_name="GeneWeaver_Alignment_Report.txt",
                mime="text/plain"
            )


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "GeneWeaver | CPU-based alignment with experimental OpenCL GPU support."
)
