
import streamlit as st
import time

from alignment import needleman_wunsch, smith_waterman
from validation import validate_dna_details

# Page settings
st.set_page_config(
    page_title="GeneWeaver",
    page_icon="🧬",
    layout="wide"
)

# Dashboard heading
st.title("🧬 GeneWeaver")
st.subheader("GPU-Accelerated CRISPR Alignment Engine")
st.write("DNA Sequence Comparison and Alignment Dashboard")

st.divider()

# Algorithm and scoring settings
st.header("Alignment Configuration")

col1, col2, col3, col4 = st.columns(4)

with col1:
    algorithm = st.selectbox(
        "Choose Algorithm",
        ["Needleman-Wunsch (Global)", "Smith-Waterman (Local)"]
    )

with col2:
    match_score = st.number_input(
        "Match Score", min_value=1, value=1, step=1
    )

with col3:
    mismatch_score = st.number_input(
        "Mismatch Penalty", max_value=0, value=-1, step=1
    )

with col4:
    gap_penalty = st.number_input(
        "Gap Penalty", max_value=0, value=-1, step=1
    )

st.divider()

# DNA input
st.header("DNA Sequence Input")

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

if st.button("🚀 Run DNA Alignment", type="primary"):

    valid1, cleaned1, message1 = validate_dna_details(sequence1)
    valid2, cleaned2, message2 = validate_dna_details(sequence2)

    if not valid1:
        st.error("Sequence 1: " + message1)

    if not valid2:
        st.error("Sequence 2: " + message2)

    if valid1 and valid2:

        st.success("Both DNA sequences are valid!")

        # Run selected algorithm
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

        # Calculate statistics
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

        # Results
        st.divider()
        st.header("Alignment Results")

        result1, result2, result3, result4 = st.columns(4)

        result1.metric("Alignment Score", score)
        result2.metric("Matches", matches)
        result3.metric("Mismatches", mismatches)
        result4.metric("Gap Columns", gaps)

        col1, col2 = st.columns(2)

        col1.metric("Sequence Identity", f"{identity:.2f}%")
        col2.metric("Execution Time", f"{execution_time:.4f} ms")

        # Colour-coded alignment
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

        st.write("**Colour Legend:**")
        st.markdown(
            """
            🟢 Green – Matching bases

            🔴 Red – Mismatching bases

            🟡 Yellow – Gaps
            """
        )

        st.success("DNA alignment completed successfully!")

st.divider()

st.caption(
    "GeneWeaver | Current algorithms run on CPU. "
    "GPU acceleration is a future development."
)
