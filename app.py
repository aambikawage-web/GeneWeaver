
import os
import time
import html

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from alignment import needleman_wunsch, smith_waterman
from validation import validate_dna_details, get_dna_statistics


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="GeneWeaver | DNA Alignment",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# DARK DASHBOARD THEME
# =====================================================

st.markdown("""
<style>

.stApp {
    background: #080d18;
    color: #f1f5f9;
}

.block-container {
    max-width: 1600px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, h4, p, label,
.stMarkdown, .stCaption {
    color: #e5edf7 !important;
}

[data-testid="stSidebar"] {
    background: #101827;
}

[data-testid="stExpander"] {
    background: #111827;
    border: 1px solid #34445c;
    border-radius: 10px;
}

[data-testid="stExpander"] summary {
    background: #1b2638;
}

[data-testid="stExpander"] summary p {
    color: white !important;
}

.stTextArea textarea,
.stTextInput input,
[data-baseweb="input"] input {
    background: #151e30 !important;
    color: white !important;
    border: 1px solid #34445c !important;
}

[data-baseweb="select"] > div {
    background: #151e30 !important;
    color: white !important;
}

[data-baseweb="select"] span {
    color: white !important;
}

[data-testid="stMetric"] {
    background: #151e30;
    border: 1px solid #34445c;
    border-radius: 10px;
    padding: 15px;
}

[data-testid="stMetricLabel"] {
    color: #9fb2c9 !important;
}

[data-testid="stMetricValue"] {
    color: white !important;
}

.stButton > button,
.stDownloadButton > button {
    background: #087eaa !important;
    color: white !important;
    border: 1px solid #16b6d4 !important;
    border-radius: 7px;
    font-weight: 600;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #0b9bc4 !important;
}

.panel {
    background: #111827;
    border: 1px solid #29384e;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 14px;
}

[data-testid="stChatMessage"] {
    background: #151e30;
    border: 1px solid #34445c;
    border-radius: 10px;
}

[data-testid="stChatInput"] textarea {
    background: #151e30 !important;
    color: white !important;
}

hr {
    border-color: #34445c !important;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# SESSION STATE
# =====================================================

if "alignment_result" not in st.session_state:
    st.session_state.alignment_result = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# =====================================================
# HEADER
# =====================================================

st.title("🧬 GeneWeaver")

st.subheader("GPU-Accelerated CRISPR Alignment Engine")

st.caption("DNA Sequence Comparison and Alignment Dashboard")

st.divider()


# =====================================================
# FASTA FILE READER
# =====================================================

def read_fasta(uploaded_file):

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


# =====================================================
# DNA INPUT
# =====================================================

st.subheader("DNA Sequence Input")

input_method = st.radio(
    "Input Method",
    ["Manual Input", "Upload FASTA File"],
    horizontal=True
)

seq1 = ""
seq2 = ""

if input_method == "Manual Input":

    col1, col2 = st.columns(2)

    with col1:
        seq1 = st.text_area(
            "First DNA Sequence",
            value="ATCGATCG",
            height=120
        )

    with col2:
        seq2 = st.text_area(
            "Second DNA Sequence",
            value="ATCGTTCG",
            height=120
        )

else:

    uploaded_file = st.file_uploader(
        "Upload FASTA file",
        type=["fasta", "fa", "txt"]
    )

    if uploaded_file:

        try:

            sequences = read_fasta(uploaded_file)

            if len(sequences) >= 2:

                seq1 = sequences[0]
                seq2 = sequences[1]

                st.success("FASTA file uploaded successfully!")

                col1, col2 = st.columns(2)

                with col1:
                    st.write("First sequence")
                    st.code(seq1)

                with col2:
                    st.write("Second sequence")
                    st.code(seq2)

                if len(sequences) > 2:
                    st.info(
                        "More than two sequences found. "
                        "The first two will be compared."
                    )

            else:
                st.error(
                    "Please upload a FASTA file containing "
                    "at least two sequences."
                )

        except UnicodeDecodeError:
            st.error("Unable to read this file. Please use a text FASTA file.")


# =====================================================
# ALIGNMENT CONFIGURATION
# =====================================================

st.divider()

st.subheader("Alignment Configuration")

c1, c2, c3, c4 = st.columns(4)

with c1:
    algorithm = st.selectbox(
        "Algorithm",
        [
            "Needleman-Wunsch (Global)",
            "Smith-Waterman (Local)"
        ]
    )

with c2:
    match_score = st.number_input(
        "Match Score",
        value=1,
        min_value=1
    )

with c3:
    mismatch_penalty = st.number_input(
        "Mismatch Penalty",
        value=-1,
        max_value=0
    )

with c4:
    gap_penalty = st.number_input(
        "Gap Penalty",
        value=-1,
        max_value=0
    )


# =====================================================
# RUN ALIGNMENT
# =====================================================

if st.button("Run DNA Alignment", type="primary"):

    valid1, clean1, message1 = validate_dna_details(seq1)
    valid2, clean2, message2 = validate_dna_details(seq2)

    if not valid1:
        st.error("Sequence 1: " + message1)

    if not valid2:
        st.error("Sequence 2: " + message2)

    if valid1 and valid2:

        start_time = time.perf_counter()

        if algorithm == "Needleman-Wunsch (Global)":

            aligned1, aligned2, score = needleman_wunsch(
                clean1,
                clean2,
                match=match_score,
                mismatch=mismatch_penalty,
                gap=gap_penalty
            )

        else:

            aligned1, aligned2, score = smith_waterman(
                clean1,
                clean2,
                match=match_score,
                mismatch=mismatch_penalty,
                gap=gap_penalty
            )

        execution_time = (
            time.perf_counter() - start_time
        ) * 1000

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
            if alignment_length else 0
        )

        st.session_state.alignment_result = {
            "algorithm": algorithm,
            "seq1": clean1,
            "seq2": clean2,
            "aligned1": aligned1,
            "aligned2": aligned2,
            "score": score,
            "matches": matches,
            "mismatches": mismatches,
            "gaps": gaps,
            "identity": identity,
            "execution_time": execution_time,
            "match_score": match_score,
            "mismatch_penalty": mismatch_penalty,
            "gap_penalty": gap_penalty
        }

        st.success("DNA alignment completed successfully!")


# =====================================================
# GET ALIGNMENT RESULTS
# =====================================================

result = st.session_state.alignment_result


# =====================================================
# CHART DATA
# =====================================================

def create_alignment_dataframe(result):

    rows = []

    for position, (a, b) in enumerate(
        zip(result["aligned1"], result["aligned2"]),
        start=1
    ):

        if a == "-" or b == "-":
            kind = "Gap"

        elif a == b:
            kind = "Match"

        else:
            kind = "Mismatch"

        rows.append({
            "Position": position,
            "Sequence 1": a,
            "Sequence 2": b,
            "Type": kind
        })

    return pd.DataFrame(rows)


COLORS = {
    "Match": "#20c65a",
    "Mismatch": "#f0b900",
    "Gap": "#ef4444"
}


# =====================================================
# ALIGNMENT COMPOSITION GRAPH
# =====================================================

def composition_chart(df):

    counts = df["Type"].value_counts()

    labels = ["Matches", "Mismatches", "Gaps"]

    values = [
        int(counts.get("Match", 0)),
        int(counts.get("Mismatch", 0)),
        int(counts.get("Gap", 0))
    ]

    colors = [
        COLORS["Match"],
        COLORS["Mismatch"],
        COLORS["Gap"]
    ]

    total = max(sum(values), 1)

    fig = go.Figure()

    for label, value, color in zip(labels, values, colors):

        fig.add_trace(go.Bar(
            x=[value],
            y=["Alignment"],
            name=label,
            orientation="h",
            marker_color=color,
            text=[f"{value} ({value / total * 100:.1f}%)"],
            textposition="inside"
        ))

    fig.update_layout(
        barmode="stack",
        height=120,
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font_color="white",
        margin=dict(l=5, r=5, t=5, b=5),
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )

    return fig


# =====================================================
# SEQUENCE COMPOSITION GRAPH
# =====================================================

def sequence_chart(result):

    bases = ["A", "T", "C", "G"]

    seq1_counts = [
        result["seq1"].count(base) for base in bases
    ]

    seq2_counts = [
        result["seq2"].count(base) for base in bases
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=bases,
        y=seq1_counts,
        name="Sequence 1",
        marker_color="#11b8d4"
    ))

    fig.add_trace(go.Bar(
        x=bases,
        y=seq2_counts,
        name="Sequence 2",
        marker_color="#a855f7"
    ))

    fig.update_layout(
        barmode="group",
        height=280,
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font_color="white",
        margin=dict(l=10, r=10, t=30, b=20),
        legend=dict(orientation="h", y=-0.2),
        yaxis=dict(gridcolor="#29384e")
    )

    return fig


# =====================================================
# SIMILARITY PROFILE GRAPH
# =====================================================

def similarity_chart(df):

    y_map = {
        "Match": 1,
        "Mismatch": 0,
        "Gap": -1
    }

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["Position"],
        y=df["Type"].map(y_map),
        mode="lines",
        name="Similarity Trend",
        line=dict(color="#17b8d1", width=1)
    ))

    for kind in ["Match", "Mismatch", "Gap"]:

        subset = df[df["Type"] == kind]

        fig.add_trace(go.Scatter(
            x=subset["Position"],
            y=subset["Type"].map(y_map),
            mode="markers",
            name=kind,
            marker=dict(
                color=COLORS[kind],
                size=8
            ),
            customdata=subset[
                ["Sequence 1", "Sequence 2"]
            ],
            hovertemplate=(
                "Position: %{x}<br>"
                "Sequence 1: %{customdata[0]}<br>"
                "Sequence 2: %{customdata[1]}<br>"
                + kind +
                "<extra></extra>"
            )
        ))

    fig.update_layout(
        height=260,
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font_color="white",
        margin=dict(l=10, r=10, t=35, b=10),
        xaxis=dict(
            title="Alignment Position",
            gridcolor="#29384e"
        ),
        yaxis=dict(
            tickvals=[-1, 0, 1],
            ticktext=["Gap", "Mismatch", "Match"],
            gridcolor="#29384e"
        ),
        legend=dict(orientation="h", y=-0.25)
    )

    return fig


# =====================================================
# ALIGNMENT REGIONS GRAPH
# =====================================================

def region_chart(df):

    fig = go.Figure()

    for kind in ["Match", "Mismatch", "Gap"]:

        subset = df[df["Type"] == kind]

        fig.add_trace(go.Bar(
            x=subset["Position"],
            y=[1] * len(subset),
            name=kind,
            marker_color=COLORS[kind],
            width=1
        ))

    fig.update_layout(
        barmode="stack",
        height=120,
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font_color="white",
        margin=dict(l=10, r=10, t=30, b=20),
        showlegend=True,
        yaxis=dict(visible=False),
        xaxis=dict(
            title="Alignment Position",
            gridcolor="#29384e"
        )
    )

    return fig


# =====================================================
# RESULTS AND VISUALIZATION DASHBOARD
# =====================================================

if result:

    df = create_alignment_dataframe(result)

    st.divider()

    st.subheader("Alignment Results")

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Alignment Score", result["score"])
    c2.metric("Matches", result["matches"])
    c3.metric("Mismatches", result["mismatches"])
    c4.metric("Gap Columns", result["gaps"])
    c5.metric("Identity", f'{result["identity"]:.2f}%')
    c6.metric("Execution Time", f'{result["execution_time"]:.4f} ms')

    st.divider()

    st.subheader("Alignment Visualization")

    # All graphs appear automatically here.

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            '<div class="panel"><h4>Alignment Composition</h4>'
            '<p style="color:#94a3b8;">Character Distribution '
            'by Alignment Type</p></div>',
            unsafe_allow_html=True
        )

        st.plotly_chart(
            composition_chart(df),
            use_container_width=True,
            config={"displayModeBar": False}
        )

        m1, m2, m3 = st.columns(3)

        m1.metric("Matches", result["matches"])
        m2.metric("Mismatches", result["mismatches"])
        m3.metric("Gaps", result["gaps"])

    with col2:

        st.markdown(
            '<div class="panel"><h4>Sequence Composition</h4></div>',
            unsafe_allow_html=True
        )

        st.plotly_chart(
            sequence_chart(result),
            use_container_width=True,
            config={"displayModeBar": False}
        )

    st.markdown(
        '<div class="panel"><h4>Similarity Profile</h4></div>',
        unsafe_allow_html=True
    )

    st.plotly_chart(
        similarity_chart(df),
        use_container_width=True,
        config={"displayModeBar": False}
    )

    st.markdown(
        '<div class="panel"><h4>Alignment Regions</h4></div>',
        unsafe_allow_html=True
    )

    st.plotly_chart(
        region_chart(df),
        use_container_width=True,
        config={"displayModeBar": False}
    )

    # =================================================
    # EXTRA VISUALIZATION VIEWS
    # =================================================

    st.divider()

    st.subheader("Additional Alignment Views")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Block View",
        "Linear View",
        "Detailed Analysis",
        "Compact View",
        "Interactive View"
    ])

    with tab1:

        st.write("Colour-coded DNA alignment")

        for start in range(0, len(df), 60):

            part = df.iloc[start:start + 60]

            line1 = ""
            line2 = ""

            for _, row in part.iterrows():

                color = COLORS[row["Type"]]

                line1 += (
                    f'<span style="color:{color};font-weight:bold;">'
                    f'{html.escape(row["Sequence 1"])}</span>'
                )

                line2 += (
                    f'<span style="color:{color};font-weight:bold;">'
                    f'{html.escape(row["Sequence 2"])}</span>'
                )

            st.markdown(
                f"""
                <div style="background:#111827;padding:12px;
                border-radius:8px;overflow-x:auto;
                font-family:monospace;font-size:17px;">
                Sequence 1: {line1}<br>
                Sequence 2: {line2}
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            "🟢 Match &nbsp;&nbsp; 🔴 Mismatch &nbsp;&nbsp; 🟡 Gap"
        )

    with tab2:

        st.write("Linear Alignment")

        st.code(
            "Sequence 1: " + result["aligned1"] +
            "\nSequence 2: " + result["aligned2"]
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    with tab3:

        st.write("Algorithm:", result["algorithm"])

        st.write("Original Sequence 1:", result["seq1"])
        st.write("Original Sequence 2:", result["seq2"])

        st.write("Aligned Sequence 1:", result["aligned1"])
        st.write("Aligned Sequence 2:", result["aligned2"])

        st.json({
            "Match Score": result["match_score"],
            "Mismatch Penalty": result["mismatch_penalty"],
            "Gap Penalty": result["gap_penalty"],
            "Alignment Score": result["score"],
            "Matches": result["matches"],
            "Mismatches": result["mismatches"],
            "Gaps": result["gaps"],
            "Identity": result["identity"]
        })

    with tab4:

        st.metric("Alignment Score", result["score"])
        st.metric("Sequence Identity", f'{result["identity"]:.2f}%')

        st.write("Algorithm:", result["algorithm"])
        st.write("Alignment Length:", len(result["aligned1"]))

    with tab5:

        position = st.slider(
            "Explore DNA alignment position",
            min_value=1,
            max_value=max(len(df), 1),
            value=1
        )

        selected = df.iloc[position - 1]

        c1, c2 = st.columns(2)

        c1.metric("Sequence 1", selected["Sequence 1"])
        c2.metric("Sequence 2", selected["Sequence 2"])

        st.info(
            f'Position {position}: {selected["Type"]}'
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


# =====================================================
# DNA STATISTICS
# =====================================================

if result:

    st.divider()

    with st.expander("DNA Sequence Statistics"):

        stats1 = get_dna_statistics(result["seq1"])
        stats2 = get_dna_statistics(result["seq2"])

        c1, c2 = st.columns(2)

        with c1:

            st.subheader("Sequence 1")

            st.write("Length:", stats1["length"])
            st.write("GC Content:", stats1["gc_content"], "%")
            st.json(stats1["counts"])

        with c2:

            st.subheader("Sequence 2")

            st.write("Length:", stats2["length"])
            st.write("GC Content:", stats2["gc_content"], "%")
            st.json(stats2["counts"])


# =====================================================
# DOWNLOAD ALIGNMENT REPORT
# =====================================================

if result:

    report = f"""
GENEWEAVER - DNA ALIGNMENT REPORT
=================================

Algorithm: {result["algorithm"]}

Original Sequence 1: {result["seq1"]}
Original Sequence 2: {result["seq2"]}

Aligned Sequence 1: {result["aligned1"]}
Aligned Sequence 2: {result["aligned2"]}

Scoring Configuration:
Match Score: {result["match_score"]}
Mismatch Penalty: {result["mismatch_penalty"]}
Gap Penalty: {result["gap_penalty"]}

Alignment Results:
Alignment Score: {result["score"]}
Matches: {result["matches"]}
Mismatches: {result["mismatches"]}
Gap Columns: {result["gaps"]}
Sequence Identity: {result["identity"]:.2f}%
Execution Time: {result["execution_time"]:.4f} ms

Generated by GeneWeaver
"""

    st.divider()

    st.download_button(
        "Download Alignment Report",
        report,
        file_name="GeneWeaver_Alignment_Report.txt",
        mime="text/plain"
    )


# =====================================================
# GENEWEAVER CHATBOT
# =====================================================

st.divider()

st.subheader("🤖 GeneWeaver AI Chat Assistant")

st.caption(
    "Ask questions about DNA, FASTA, alignment algorithms "
    "and your alignment results."
)


def offline_answer(question):

    q = question.lower()

    if "needleman" in q or "global" in q:

        return (
            "Needleman-Wunsch is a global alignment algorithm. "
            "It compares complete DNA sequences using match, "
            "mismatch and gap scores."
        )

    if "smith" in q or "local" in q:

        return (
            "Smith-Waterman is a local alignment algorithm. "
            "It finds the best matching region between two sequences."
        )

    if "fasta" in q:

        return (
            "FASTA is a text format for biological sequences. "
            "Each sequence starts with a header beginning with >."
        )

    if "gc" in q:

        return (
            "GC content measures the percentage of G and C bases. "
            "Formula: (G + C) / Total Length × 100."
        )

    if "identity" in q:

        return (
            "Sequence identity is the percentage of matching "
            "alignment positions."
        )

    if "crisp" in q:

        return (
            "CRISPR is a genome-editing technology. GeneWeaver "
            "currently provides DNA sequence validation and "
            "pairwise alignment, not clinical editing predictions."
        )

    if "score" in q or "result" in q:

        if st.session_state.alignment_result:

            r = st.session_state.alignment_result

            return (
                f"Your current alignment score is {r['score']}. "
                f"Matches: {r['matches']}, "
                f"Mismatches: {r['mismatches']}, "
                f"Gaps: {r['gaps']}, "
                f"Identity: {r['identity']:.2f}%."
            )

        return "Please run a DNA alignment first."

    if "match" in q or "mismatch" in q or "gap" in q:

        return (
            "A match means two bases are identical. "
            "A mismatch means they differ. "
            "A gap is represented by the '-' character."
        )

    return (
        "Hello! I am GeneWeaver Assistant. I can explain "
        "DNA alignment, FASTA files, Needleman-Wunsch, "
        "Smith-Waterman, GC content, matches, mismatches and gaps."
    )


def get_ai_answer(question):

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return offline_answer(question)

    try:

        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are GeneWeaver Assistant. "
                        "Explain DNA alignment, biology and algorithms "
                        "in simple language. Do not provide medical "
                        "or clinical advice."
                    )
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        return response.choices[0].message.content

    except Exception:

        return (
            "The AI service is currently unavailable. "
            + offline_answer(question)
        )


for message in st.session_state.chat_history:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


question = st.chat_input(
    "Ask GeneWeaver something..."
)

if question:

    st.session_state.chat_history.append({
        "role": "user",
        "content": question
    })

    answer = get_ai_answer(question)

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": answer
    })

    st.rerun()


if st.button("Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(
    "GeneWeaver | DNA Sequence Alignment | "
    "Experimental OpenCL GPU Support"
)
