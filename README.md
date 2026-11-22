# 🧬 GeneWeaver
### GPU-Accelerated CRISPR Alignment Engine

GeneWeaver is a Python-based DNA sequence alignment project that implements global and local DNA sequence alignment algorithms and explores GPU computing using OpenCL.

The project compares DNA sequences, identifies matching regions, calculates alignment scores, analyzes nucleotide composition, and visualizes CPU and experimental GPU performance through an interactive Streamlit dashboard.

## 🚀 Features

- DNA sequence validation and normalization.
- Global alignment using the Needleman-Wunsch algorithm.
- Local alignment using the Smith-Waterman algorithm.
- Custom match, mismatch, and gap scoring.
- FASTA file upload and sequence parsing.
- DNA nucleotide statistics (A, T, C, G).
- GC-content calculation.
- Alignment score, matches, mismatches, and gaps.
- Sequence identity and execution-time calculation.
- Color-coded DNA alignment results.
- Interactive Streamlit dashboard.
- Comparative performance charts.
- Alignment report generation and download.
- CPU performance benchmarking.
- Experimental OpenCL GPU alignment.
- Unit testing using Python unittest.
- GeneWeaver chatbot interface for project-related questions.

**Note:** Generative AI API integration for dynamic chatbot responses is a planned enhancement and is not yet confirmed as operational.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core development |
| Streamlit | Interactive dashboard |
| OpenCL | Experimental GPU computing |
| PyOpenCL | Python interface for OpenCL |
| NumPy | Numerical operations |
| Pandas | Data handling |
| Unittest | Software testing |
| Git and GitHub | Version control |

## 🧬 Alignment Algorithms

### 1. Needleman-Wunsch Algorithm

Performs global DNA sequence alignment by comparing two complete sequences using dynamic programming.

### 2. Smith-Waterman Algorithm

Performs local DNA sequence alignment to identify the best matching region between two DNA sequences.

Both algorithms support configurable match, mismatch, and gap scoring values.

## 📂 FASTA File Support

GeneWeaver supports uploading DNA sequence files in FASTA format.

- Upload `.fasta`, `.fa`, or `.txt` files.
- Read and extract DNA sequences.
- Display sequence information.
- Compare the first two sequences for alignment.

## 📊 DNA Sequence Analysis

The project provides:

- Total sequence length.
- Adenine (A) count.
- Thymine (T) count.
- Cytosine (C) count.
- Guanine (G) count.
- GC-content percentage.
- Alignment score and comparison statistics.

## 📈 Interactive Dashboard

The Streamlit dashboard provides:

- Manual DNA sequence input.
- FASTA file upload.
- Global and local alignment selection.
- Configurable scoring parameters.
- Color-coded alignment visualization.
- DNA statistics.
- Comparative charts.
- Alignment report download.
- Chatbot interface.

## ⚡ GPU Implementation

GeneWeaver includes an experimental OpenCL-based GPU prototype for Needleman-Wunsch alignment.

- Uses Intel integrated graphics through OpenCL.
- Calculates dynamic programming matrix cells using anti-diagonal wavefront processing.
- Performs traceback on the CPU.
- Compares GPU and CPU alignment scores.

**Hardware note:** GPU execution was tested using Intel Iris Xe integrated graphics. NVIDIA CUDA is not required.

GPU execution may be slower for smaller sequences because of OpenCL initialization and kernel-launch overhead.

## 📊 Performance Benchmarking

Example results from an earlier test run:

| Sequence Length | CPU Time (ms) | GPU Time (ms) |
|---:|---:|---:|
| 20 | 0.1731 | 35.0258 |
| 40 | 0.5745 | 11.5377 |
| 80 | 1.9964 | 16.5995 |

These results show that the experimental GPU implementation was slower for these small test inputs. Further optimization is required.

## 🤖 Chatbot and Future Generative AI Integration

GeneWeaver includes a chatbot interface designed to help users understand DNA alignment concepts and project features.

Planned improvements include:

- OpenAI API integration.
- Dynamic AI-generated responses.
- Better explanations of DNA alignment algorithms.
- Context-aware answers about GeneWeaver.

Generative AI functionality will be added and tested separately.

## 📁 Project Structure

```text
GeneWeaver/
├── alignment.py
├── validation.py
├── main.py
├── app.py
├── gpu_alignment.py
├── benchmark.py
├── benchmark_gpu.py
├── test_alignment.py
├── sample_sequences.fasta
├── README.md
└── .gitignore
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/aambikawage-web/GeneWeaver.git
cd GeneWeaver
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment on Windows

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install streamlit numpy pandas
```

For experimental GPU execution, install an appropriate OpenCL runtime for your hardware and PyOpenCL:

```bash
python -m pip install pyopencl
```

## ▶️ Run the Project

### Launch the Streamlit dashboard

```bash
python -m streamlit run app.py
```

### Run the command-line engine

```bash
python main.py
```

### Run CPU benchmarks

```bash
python benchmark.py
```

### Run GPU benchmarks

```bash
python benchmark_gpu.py
```

### Run unit tests

```bash
python -m unittest -v test_alignment.py
```

The current alignment test suite contains six tests covering global and local alignment.

## 🔮 Future Enhancements

- Complete OpenAI API integration for generative AI chatbot responses.
- Improve chatbot knowledge of DNA and CRISPR concepts.
- Optimize GPU kernel execution.
- Reduce OpenCL setup overhead.
- Explore GPU acceleration for Smith-Waterman.
- Support larger DNA sequence datasets.
- Improve dashboard visualizations.
- Add more validation and edge-case tests.
- Explore CRISPR guide RNA matching and analysis.

## 👩‍💻 Developer

**Ambika Wage**

GitHub: https://github.com/aambikawage-web

---

*GeneWeaver — Exploring DNA sequence alignment through Python and GPU computing.*
