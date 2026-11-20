
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime

from alignment import needleman_wunsch, smith_waterman
from validation import validate_dna_details, get_dna_statistics


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="GeneWeaver | DNA Alignment",
    page_icon="🧬",
    layout="wide"
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background-color: #080d19;
    color: #f1f5f9;
}

h1, h2, h3, h4, p, label {
    color: #f1f5f9 !important;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

div[data-testid="stMetric"] {
    background: #172236;
    border: 1px solid #34445e;
    padding: 18px;
    border-radius: 12px;
}

div[data-testid="stMetric"] label {
    color: #dbeafe !important;
}

div[data-testid="stMetricValue"] {
    color: #ffffff !important;
}

.stTextInput input,
.stTextArea textarea {
    background-color: #172236 !important;
    color: white !important;
    border: 1px solid #52627a !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #aab7ca !important;
}

.stButton button,
.stFormSubmitButton button {
    background-color: #078bb5;
    color: white;
    border-radius: 8px;
    border: none;
    font-weight: bold;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    background-color: #06a6d3;
    color: white;
}

section[data-testid="stSidebar"] {
    background-color: #111a2b;
}

.chat-message {
    background-color: #172236;
    border: 1px solid #34445e;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 10px;
}

hr {
    border-color: #34445e;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "alignment_result" not in st.session_state:
    st.session_state.alignment_result = None

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I am GeneWeaver Help Assistant. "
                "Ask me about DNA alignment, FASTA files, "
                "GC content, or the project."
            )
        }
    ]


# --------------------------------------------------
# FASTA FILE READER
# --------------------------------------------------

def read_fasta(uploaded_file):
    content = uploaded_file.getvalue().decode("utf-8")

    records = []
    current_name = None
    current_sequence = []

    for line in content.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith(">"):
            if current_name is not None:
                records.append((
                    current_name,
                    "".join(current_sequence)
                ))

            current_name = line[1:].strip() or "Unnamed sequence"
            current_sequence = []

        else:
            if current_name is None:
                current_name = "Sequence 1"

            current_sequence.append(line)

    if current_name is not None:
        records.append((
            current_name,
            "".join(current_sequence)
        ))

    return records


# --------------------------------------------------
# CHATBOT RESPONSE
# --------------------------------------------------

def chatbot_response(question):
    q = question.lower().strip()

    if not q:
        return "Please enter a question."

    if any(word in q for word in ["hello", "hi", "hey"]):
        return (
            "Hello! Welcome to GeneWeaver. "
            "I can help you understand DNA alignment "
            "and the features of this project."
        )

    if "needleman" in q or "global alignment" in q:
        return (
            "Needleman-Wunsch is a global DNA sequence "
            "alignment algorithm. It compares two complete "
            "sequences and finds the best overall alignment."
        )

    if "smith" in q or "local alignment" in q:
        return (
            "Smith-Waterman is a local alignment algorithm. "
            "It identifies the best matching region between "
            "two DNA sequences."
        )

    if "alignment" in q:
        return (
            "DNA sequence alignment compares DNA sequences "
            "to identify matching bases, mismatches, and gaps. "
            "GeneWeaver supports global and local alignment."
        )

    if "gc content" in q or "gc%" in q:
        return (
            "GC content is the percentage of G (guanine) "
            "and C (cytosine) bases in a DNA sequence. "
            "Formula: ((G + C) / Total bases) × 100."
        )

    if "fasta" in q:
        return (
            "FASTA is a text format used to store biological "
            "sequences. A sequence starts with a header line "
            "beginning with >, followed by the DNA sequence."
        )

    if "gpu" in q or "opencl" in q:
        return (
            "GeneWeaver includes experimental OpenCL support "
            "for GPU-based alignment. Performance depends on "
            "sequence length and hardware. Small sequences "
            "may run faster on the CPU because GPU setup has overhead."
        )

    if "crisp" in q:
        return (
            "CRISPR is a gene-editing technology. GeneWeaver "
            "is an educational DNA sequence alignment project "
            "that compares sequences; it does not perform gene editing."
        )

    if "match" in q or "mismatch" in q:
        return (
            "A match occurs when two aligned DNA bases are the same. "
            "A mismatch occurs when the bases are different."
        )

    if "project" in q or "geneweaver" in q:
        return (
            "GeneWeaver is a Python-based DNA sequence alignment "
            "project. It includes Needleman-Wunsch global alignment, "
            "Smith-Waterman local alignment, DNA validation, "
            "statistics, visualizations, and experimental OpenCL support."
        )

    if "help" in q or "features" in q:
        return (
            "GeneWeaver features include manual DNA input, FASTA upload, "
            "global and local alignment, alignment scores, DNA statistics, "
            "charts, downloadable reports, and experimental OpenCL support."
        )

    return (
        "I can help with DNA alignment, Needleman-Wunsch, "
        "Smith-Waterman, FASTA files, GC content, DNA statistics, "
        "CRISPR, and GeneWeaver project features. "
        "Please try asking about one of these topics."
    )


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    "<h1 style='font-size:45px;'>🧬 GeneWeaver</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "## GPU-Accelerated CRISPR Alignment Engine"
)

st.caption("DNA Sequence Comparison and Alignment Dashboard")

st.divider()


# --------------------------------------------------
# DNA INPUT
# --------------------------------------------------

st.header("DNA Sequence Input")

input_method = st.radio(
    "Input Method",
    ["Manual Input", "Upload FASTA File"],
    horizontal=True
)

seq1 = ""
seq2 = ""
sequence_names = ["Sequence 1", "Sequence 2"]

if input_method == "Manual Input":

    col1, col2 = st.columns(2)

    with col1:
        seq1 = st.text_area(
            "First DNA Sequence",
            value="ATCGATCG",
            height=110
        )

    with col2:
        seq2 = st.text_area(
            "Second DNA Sequence",
            value="ATCGTTCG",
            height=110
        )

else:
    uploaded_file = st.file_uploader(
        "Upload FASTA file",
        type=["fasta", "fa", "txt"]
    )

    if uploaded_file is not None:
        try:
            records = read_fasta(uploaded_file)

            if len(records) < 2:
                st.error("Please upload a FASTA file containing at least two sequences.")

            else:
                sequence_names = [
                    records[0][0],
                    records[1][0]
                ]

                seq1 = records[0][1]
                seq2 = records[1][1]

                st.success(
                    f"Loaded {len(records)} sequence(s). "
                    "The first two will be compared."
                )

                st.text_area(
                    "First DNA Sequence",
                    value=seq1,
                    height=80,
                    disabled=True
                )

                st.text_area(
                    "Second DNA Sequence",
                    value=seq2,
                    height=80,
                    disabled=True
                )

        except Exception as error:
            st.error(f"Could not read FASTA file: {error}")


# --------------------------------------------------
# ALIGNMENT CONFIGURATION
# --------------------------------------------------

st.divider()
st.header("Alignment Configuration")

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
        step=1
    )

with c3:
    mismatch_penalty = st.number_input(
        "Mismatch Penalty",
        value=-1,
        step=1
    )

with c4:
    gap_penalty = st.number_input(
        "Gap Penalty",
        value=-1,
        step=1
    )


# --------------------------------------------------
# RUN ALIGNMENT
# --------------------------------------------------

if st.button("Run DNA Alignment", type="primary"):

    valid1, clean1, message1 = validate_dna_details(seq1)
    valid2, clean2, message2 = validate_dna_details(seq2)

    if not valid1:
        st.error(f"First sequence: {message1}")

    elif not valid2:
        st.error(f"Second sequence: {message2}")

    else:
        try:
            start_time = time.perf_counter()

            if algorithm.startswith("Needleman"):
                aligned1, aligned2, score = needleman_wunsch(
                    clean1,
                    clean2,
                    int(match_score),
                    int(mismatch_penalty),
                    int(gap_penalty)
                )
            else:
                aligned1, aligned2, score = smith_waterman(
                    clean1,
                    clean2,
                    int(match_score),
                    int(mismatch_penalty),
                    int(gap_penalty)
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

            total_columns = len(aligned1)

            identity = (
                (matches / total_columns) * 100
                if total_columns else 0
            )

            st.session_state.alignment_result = {
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
                "algorithm": algorithm,
                "name1": sequence_names[0],
                "name2": sequence_names[1]
            }

            st.success("DNA alignment completed successfully!")

        except Exception as error:
            st.error(f"Alignment error: {error}")


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

result = st.session_state.alignment_result

if result is not None:

    st.divider()
    st.header("Alignment Results")

    m1, m2, m3, m4, m5, m6 = st.columns(6)

    m1.metric("Alignment Score", result["score"])
    m2.metric("Matches", result["matches"])
    m3.metric("Mismatches", result["mismatches"])
    m4.metric("Gap Columns", result["gaps"])
    m5.metric("Identity", f'{result["identity"]:.2f}%')
    m6.metric("Execution Time", f'{result["execution_time"]:.4f} ms')

    st.subheader("Alignment Visualization")

    aligned1 = result["aligned1"]
    aligned2 = result["aligned2"]

    # Alignment composition chart

    composition = pd.DataFrame({
        "Type": ["Matches", "Mismatches", "Gaps"],
        "Count": [
            result["matches"],
            result["mismatches"],
            result["gaps"]
        ]
    })

    fig1 = px.bar(
        composition,
        x="Count",
        y="Type",
        orientation="h",
        color="Type",
        title="Alignment Composition",
        text="Count",
        color_discrete_map={
            "Matches": "#20c55e",
            "Mismatches": "#ef4444",
            "Gaps": "#eab308"
        }
    )

    fig1.update_layout(
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font_color="white"
    )

    # Sequence composition chart

    stats1 = get_dna_statistics(result["seq1"])
    stats2 = get_dna_statistics(result["seq2"])

    bases = ["A", "T", "C", "G"]

    composition_data = pd.DataFrame({
        "Base": bases,
        "Sequence 1": [stats1["counts"][b] for b in bases],
        "Sequence 2": [stats2["counts"][b] for b in bases]
    })

    fig2 = go.Figure()

    fig2.add_trace(go.Bar(
        x=bases,
        y=composition_data["Sequence 1"],
        name="Sequence 1"
    ))

    fig2.add_trace(go.Bar(
        x=bases,
        y=composition_data["Sequence 2"],
        name="Sequence 2"
    ))

    fig2.update_layout(
        title="Sequence Composition",
        barmode="group",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font_color="white"
    )

    # Similarity profile

    positions = list(range(1, len(aligned1) + 1))

    similarity = [
        1 if a == b and a != "-" else 0
        for a, b in zip(aligned1, aligned2)
    ]

    fig3 = go.Figure()

    fig3.add_trace(go.Scatter(
        x=positions,
        y=similarity,
        mode="lines+markers",
        name="Similarity",
        line=dict(color="#06b6d4")
    ))

    fig3.update_layout(
        title="Similarity Profile",
        xaxis_title="Alignment Position",
        yaxis=dict(
            tickvals=[0, 1],
            ticktext=["Mismatch / Gap", "Match"]
        ),
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font_color="white"
    )

    # Alignment regions

    region_values = []

    for a, b in zip(aligned1, aligned2):
        if a == "-" or b == "-":
            region_values.append("Gap")
        elif a == b:
            region_values.append("Match")
        else:
            region_values.append("Mismatch")

    region_df = pd.DataFrame({
        "Position": positions,
        "Region": region_values,
        "Value": [1] * len(positions)
    })

    fig4 = px.bar(
        region_df,
        x="Position",
        y="Value",
        color="Region",
        title="Alignment Regions",
        color_discrete_map={
            "Match": "#20c55e",
            "Mismatch": "#ef4444",
            "Gap": "#eab308"
        }
    )

    fig4.update_layout(
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font_color="white",
        showlegend=True
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig3, use_container_width=True)

    with chart_col2:
        st.plotly_chart(fig2, use_container_width=True)
        st.plotly_chart(fig4, use_container_width=True)

    # Alignment views

    st.divider()
    st.header("Additional Alignment Views")

    tab1, tab2, tab3 = st.tabs([
        "Block View",
        "Linear View",
        "Detailed Analysis"
    ])

    with tab1:
        st.markdown("**Colour-coded DNA alignment**")

        colored1 = []
        colored2 = []

        for a, b in zip(aligned1, aligned2):
            if a == "-" or b == "-":
                color = "#eab308"
            elif a == b:
                color = "#20c55e"
            else:
                color = "#ef4444"

            colored1.append(
                f'<span style="color:{color};font-weight:bold">{a}</span>'
            )

            colored2.append(
                f'<span style="color:{color};font-weight:bold">{b}</span>'
            )

        st.markdown(
            f"""
            <div style="background:#172236;padding:18px;border-radius:10px;
            font-family:monospace;font-size:18px;overflow-x:auto;">
            Sequence 1: {"".join(colored1)}<br>
            Sequence 2: {"".join(colored2)}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption(
            "Green = Match | Red = Mismatch | Yellow = Gap"
        )

    with tab2:
        st.code(
            f"Sequence 1: {aligned1}\n"
            f"Sequence 2: {aligned2}",
            language="text"
        )

    with tab3:
        st.write("**Algorithm:**", result["algorithm"])
        st.write("**Alignment score:**", result["score"])
        st.write("**Matches:**", result["matches"])
        st.write("**Mismatches:**", result["mismatches"])
        st.write("**Gaps:**", result["gaps"])
        st.write("**Sequence identity:**", f'{result["identity"]:.2f}%')

    # DNA statistics

    st.divider()
    st.header("DNA Statistics")

    s1, s2 = st.columns(2)

    with s1:
        st.subheader("Sequence 1")
        st.write("Length:", stats1["length"])
        st.write("Nucleotide counts:", stats1["counts"])
        st.write("GC content:", f'{stats1["gc_content"]}%')

    with s2:
        st.subheader("Sequence 2")
        st.write("Length:", stats2["length"])
        st.write("Nucleotide counts:", stats2["counts"])
        st.write("GC content:", f'{stats2["gc_content"]}%')

    # Download report

    report = f"""
GENEWEAVER DNA ALIGNMENT REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Algorithm: {result["algorithm"]}

Original Sequence 1:
{result["seq1"]}

Original Sequence 2:
{result["seq2"]}

Aligned Sequence 1:
{aligned1}

Aligned Sequence 2:
{aligned2}

Alignment Score: {result["score"]}
Matches: {result["matches"]}
Mismatches: {result["mismatches"]}
Gaps: {result["gaps"]}
Identity: {result["identity"]:.2f}%
Execution Time: {result["execution_time"]:.4f} ms

Sequence 1 Statistics:
{stats1}

Sequence 2 Statistics:
{stats2}
"""

    st.download_button(
        "Download Alignment Report",
        data=report,
        file_name="GeneWeaver_Alignment_Report.txt",
        mime="text/plain"
    )



# --------------------------------------------------
# GENEWEAVER CHAT ASSISTANT
# --------------------------------------------------

st.divider()
st.header("🤖 GeneWeaver AI Chat Assistant")

st.write("Ask questions about DNA, FASTA, alignment algorithms and your alignment results.")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

def get_chat_answer(question):
    q = question.lower()

    if "needleman" in q or "global alignment" in q:
        return "Needleman-Wunsch performs global alignment of two complete DNA sequences."

    elif "smith" in q or "local alignment" in q:
        return "Smith-Waterman identifies the best local matching region between DNA sequences."

    elif "gc content" in q:
        return "GC content is the percentage of G and C bases in a DNA sequence."

    elif "fasta" in q:
        return "FASTA is a text format for storing DNA sequences. Headers begin with >."

    elif "gpu" in q or "opencl" in q:
        return "GeneWeaver has experimental OpenCL support for GPU-based DNA alignment."

    elif "crisp" in q:
        return "CRISPR is a gene-editing technology. GeneWeaver focuses on DNA sequence comparison."

    elif "alignment" in q or "dna" in q:
        return "DNA alignment compares sequences to identify matches, mismatches and gaps."

    else:
        return "Please ask about DNA, FASTA, GC content, Needleman-Wunsch, Smith-Waterman or CRISPR."


# Show previous conversation
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# One input and one send button
with st.form("geneweaver_chat", clear_on_submit=True):

    question = st.text_area(
        "Enter your question",
        placeholder="Example: What is DNA alignment?",
        height=80,
        key="chat_message_box"
    )

    send = st.form_submit_button("Send Message")

    if send:
        if question.strip():
            st.session_state.chat_messages.append({
                "role": "user",
                "content": question.strip()
            })

            answer = get_chat_answer(question)

            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": answer
            })

            st.rerun()
        else:
            st.warning("Please enter a question.")



# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "GeneWeaver | Python DNA Sequence Alignment Project "
    "| Experimental OpenCL support"
)

# -------- GENEWEAVER CHAT ASSISTANT --------

st.divider()
st.header("🤖 GeneWeaver AI Chat Assistant")

st.write(
    "Ask questions about DNA, FASTA, alignment algorithms "
    "and your alignment results."
)

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "chat_question" not in st.session_state:
    st.session_state.chat_question = ""

# Display previous messages
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


def get_chat_answer(question):
    q = question.lower()

    if "dna" in q or "alignment" in q:
        return "DNA alignment compares two DNA sequences to identify matches, mismatches and gaps."

    elif "fasta" in q:
        return "FASTA is a text format used to store DNA or protein sequences. Headers start with >."

    elif "gc content" in q:
        return "GC content is the percentage of G and C bases in a DNA sequence."

    elif "needleman" in q:
        return "Needleman-Wunsch performs global alignment of two complete sequences."

    elif "smith" in q:
        return "Smith-Waterman identifies the best local matching region between sequences."

    elif "crisp" in q:
        return "CRISPR is a gene-editing technology. GeneWeaver focuses on DNA sequence comparison."

    else:
        return "I can answer questions about DNA, FASTA, GC content, Needleman-Wunsch and Smith-Waterman."


# Normal text input, outside a form
question = st.text_input(
    "Type your question here",
    key="geneweaver_question_input",
    placeholder="Example: What is DNA alignment?"
)

if st.button("Send Message", key="geneweaver_send_button"):

    if question.strip():
        st.session_state.chat_messages.append({
            "role": "user",
            "content": question.strip()
        })

        answer = get_chat_answer(question)

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": answer
        })

        st.rerun()
    else:
        st.warning("Please type a question.")
