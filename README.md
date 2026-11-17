
# 🧬 GeneWeaver
### GPU-Accelerated CRISPR Alignment Engine

GeneWeaver is a Python-based DNA sequence alignment project that implements global and local sequence alignment algorithms and explores GPU computing using OpenCL.

The project aims to compare DNA sequences, identify matching regions, calculate alignment scores, and study CPU and GPU execution performance.

## 🚀 Features

- DNA sequence validation and normalization.
- Global alignment using Needleman-Wunsch algorithm.
- Local alignment using Smith-Waterman algorithm.
- Custom match, mismatch, and gap scoring.
- Interactive Streamlit dashboard.
- Color-coded DNA alignment results.
- DNA nucleotide statistics (A, T, C, G).
- GC-content calculation.
- CPU performance benchmarking.
- OpenCL GPU-based alignment prototype.
- Unit testing using Python unittest.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core development |
| Streamlit | Interactive dashboard |
| OpenCL | GPU computing |
| PyOpenCL | Python interface for OpenCL |
| NumPy | Numerical operations |
| Unittest | Software testing |
| Git & GitHub | Version control |

## 🧬 Alignment Algorithms

### 1. Needleman-Wunsch
Performs global DNA sequence alignment by comparing two complete sequences using dynamic programming.

### 2. Smith-Waterman
Performs local DNA sequence alignment to identify the best matching region between two DNA sequences.

## ⚡ GPU Implementation

GeneWeaver includes an OpenCL-based GPU prototype for Needleman-Wunsch alignment.

- Uses Intel integrated graphics through OpenCL.
- Calculates dynamic programming matrix cells using anti-diagonal wavefront processing.
- Performs traceback on the CPU.
- Compares GPU and CPU alignment scores.

**Hardware note:** GPU execution was tested using Intel Iris Xe integrated graphics. NVIDIA CUDA is not required for this implementation.

## 📊 Performance Benchmarking

Example results from an earlier test run:

| Sequence Length | CPU Time (ms) | GPU Time (ms) |
|---:|---:|---:|
| 20 | 0.1731 | 35.0258 |
| 40 | 0.5745 | 11.5377 |
| 80 | 1.9964 | 16.5995 |

GPU execution was slower for these small test inputs because of OpenCL setup and kernel-launch overhead. Further optimization is required.

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
├── README.md
└── .gitignore
```

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/aambikawage-web/GeneWeaver.git
cd GeneWeaver
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install the dashboard dependency:

```bash
python -m pip install streamlit
```

For GPU execution, install an OpenCL runtime appropriate for your hardware and PyOpenCL:

```bash
python -m pip install pyopencl numpy
```

## ▶️ Run the Project

Run the command-line engine:

```bash
python main.py
```

Launch the Streamlit dashboard:

```bash
python -m streamlit run app.py
```

Run CPU benchmarks:

```bash
python benchmark.py
```

Run GPU benchmarks in an environment with a working OpenCL runtime:

```bash
python benchmark_gpu.py
```

## 🧪 Testing

Run the unit tests:

```bash
python -m unittest -v test_alignment.py
```

The current alignment test suite contains six tests covering global and local alignment.

## 🔮 Future Enhancements

- Optimize GPU kernel execution.
- Reduce OpenCL setup overhead.
- Explore GPU acceleration for Smith-Waterman.
- Add larger DNA sequence benchmarking.
- Improve dashboard visualizations.
- Add more validation and edge-case tests.
- Explore CRISPR guide RNA matching and analysis.

## 👩‍💻 Developer

**Ambika Wage**

GitHub: [aambikawage-web](https://github.com/aambikawage-web)

---

*GeneWeaver — Exploring DNA sequence alignment through Python and GPU computing.*
