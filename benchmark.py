
# GeneWeaver - Repeated CPU Benchmark

import time
import random
import statistics

from alignment import needleman_wunsch, smith_waterman


def generate_dna(length):
    return "".join(random.choices("ATCG", k=length))


def measure_execution(function, seq1, seq2, repeats=5):

    times = []

    # Warm-up
    function(seq1, seq2)

    for _ in range(repeats):
        start = time.perf_counter()
        function(seq1, seq2)
        end = time.perf_counter()

        times.append((end - start) * 1000)

    return statistics.mean(times), statistics.median(times)


def run_benchmark():

    print("\n======================================")
    print(" GENEWEAVER REPEATED CPU BENCHMARK")
    print("======================================")

    lengths = [50, 100, 200, 400, 800]

    algorithms = [
        ("Needleman-Wunsch", needleman_wunsch),
        ("Smith-Waterman", smith_waterman)
    ]

    for name, function in algorithms:

        print(f"\n{name}")
        print("-" * 65)
        print(f"{'Length':<12}{'Average (ms)':<18}{'Median (ms)':<18}")

        for length in lengths:

            seq1 = generate_dna(length)
            seq2 = generate_dna(length)

            average, median = measure_execution(
                function, seq1, seq2
            )

            print(
                f"{length:<12}"
                f"{average:<18.4f}"
                f"{median:<18.4f}"
            )

    print("\nRepeated CPU benchmark completed!")


if __name__ == "__main__":
    run_benchmark()
