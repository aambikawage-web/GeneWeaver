
# GeneWeaver - CPU vs GPU Benchmark

import time
import random
import statistics

from alignment import needleman_wunsch
from gpu_alignment import gpu_needleman_wunsch


def generate_dna(length):
    return "".join(random.choices("ATCG", k=length))


def measure_cpu(seq1, seq2, repeats=3):
    times = []

    for _ in range(repeats):
        start = time.perf_counter()
        needleman_wunsch(seq1, seq2)
        end = time.perf_counter()

        times.append((end - start) * 1000)

    return statistics.mean(times)


def measure_gpu(seq1, seq2, repeats=3):
    times = []

    for _ in range(repeats):
        start = time.perf_counter()
        gpu_needleman_wunsch(seq1, seq2)
        end = time.perf_counter()

        times.append((end - start) * 1000)

    return statistics.mean(times)


def run_benchmark():

    random.seed(42)

    print("\n======================================")
    print(" GENEWEAVER CPU vs GPU BENCHMARK")
    print("======================================")

    # Warm-up GPU before measuring
    print("\nGPU warm-up...")
    gpu_needleman_wunsch("ATCG", "ATCG")

    lengths = [20, 40, 80]

    print("\n{:<12}{:<18}{:<18}".format(
        "Length", "CPU (ms)", "GPU (ms)"
    ))

    print("-" * 48)

    for length in lengths:

        seq1 = generate_dna(length)
        seq2 = generate_dna(length)

        cpu_time = measure_cpu(seq1, seq2)
        gpu_time = measure_gpu(seq1, seq2)

        print("{:<12}{:<18.4f}{:<18.4f}".format(
            length, cpu_time, gpu_time
        ))

        # Verify scores
        cpu_result = needleman_wunsch(seq1, seq2)
        gpu_result = gpu_needleman_wunsch(seq1, seq2)

        print("Scores match:", cpu_result[2] == gpu_result[2])
        print()

    print("Benchmark completed!")


if __name__ == "__main__":
    run_benchmark()
