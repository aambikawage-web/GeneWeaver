
# GeneWeaver - GPU Accelerated Needleman-Wunsch

import numpy as np
import pyopencl as cl


def gpu_needleman_wunsch(seq1, seq2, match=1, mismatch=-1, gap=-1):

    m = len(seq1)
    n = len(seq2)

    # Convert DNA letters into numeric values
    base_map = {"A": 0, "T": 1, "C": 2, "G": 3}

    a = np.array([base_map[x] for x in seq1], dtype=np.int32)
    b = np.array([base_map[x] for x in seq2], dtype=np.int32)

    # Create and initialize scoring matrix
    matrix = np.zeros((m + 1, n + 1), dtype=np.int32)

    matrix[:, 0] = np.arange(m + 1) * gap
    matrix[0, :] = np.arange(n + 1) * gap

    # Find Intel GPU
    devices = [
        device
        for platform in cl.get_platforms()
        for device in platform.get_devices()
        if device.type & cl.device_type.GPU
    ]

    if not devices:
        raise RuntimeError("No OpenCL GPU detected.")

    device = devices[0]

    print("GPU Device:", device.name)

    context = cl.Context([device])
    queue = cl.CommandQueue(context)

    mf = cl.mem_flags

    a_buf = cl.Buffer(
        context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a
    )

    b_buf = cl.Buffer(
        context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=b
    )

    h_buf = cl.Buffer(
        context, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=matrix
    )

    # OpenCL GPU kernel
    kernel_code = """
    __kernel void calculate_diagonal(
        __global const int *a,
        __global const int *b,
        __global int *H,
        const int m,
        const int n,
        const int start_i,
        const int diagonal,
        const int match,
        const int mismatch,
        const int gap
    ) {
        int i = start_i + get_global_id(0);
        int j = diagonal - i;

        if (i <= m && j >= 1 && j <= n) {

            int score = (a[i-1] == b[j-1])
                        ? match : mismatch;

            int diagonal_score =
                H[(i-1)*(n+1) + (j-1)] + score;

            int up =
                H[(i-1)*(n+1) + j] + gap;

            int left =
                H[i*(n+1) + (j-1)] + gap;

            H[i*(n+1) + j] =
                max(diagonal_score, max(up, left));
        }
    }
    """

    program = cl.Program(context, kernel_code).build()

    # Reuse one kernel instance
    gpu_kernel = cl.Kernel(program, "calculate_diagonal")

    # Calculate the matrix diagonal by diagonal
    for diagonal in range(2, m + n + 1):

        start_i = max(1, diagonal - n)
        end_i = min(m, diagonal - 1)

        count = end_i - start_i + 1

        if count > 0:

            gpu_kernel(
                queue,
                (count,),
                None,
                a_buf,
                b_buf,
                h_buf,
                np.int32(m),
                np.int32(n),
                np.int32(start_i),
                np.int32(diagonal),
                np.int32(match),
                np.int32(mismatch),
                np.int32(gap)
            )

    # Copy GPU matrix back to CPU
    cl.enqueue_copy(queue, matrix, h_buf).wait()

    # Perform traceback on CPU
    aligned1 = ""
    aligned2 = ""

    i, j = m, n

    while i > 0 or j > 0:

        if i > 0 and j > 0:

            score = (
                match if seq1[i - 1] == seq2[j - 1]
                else mismatch
            )

            if matrix[i, j] == matrix[i - 1, j - 1] + score:

                aligned1 = seq1[i - 1] + aligned1
                aligned2 = seq2[j - 1] + aligned2

                i -= 1
                j -= 1
                continue

        if i > 0 and matrix[i, j] == matrix[i - 1, j] + gap:

            aligned1 = seq1[i - 1] + aligned1
            aligned2 = "-" + aligned2

            i -= 1

        else:

            aligned1 = "-" + aligned1
            aligned2 = seq2[j - 1] + aligned2

            j -= 1

    return aligned1, aligned2, int(matrix[m, n])


if __name__ == "__main__":

    sequence1 = "ACACACTA"
    sequence2 = "AGCACACA"

    result = gpu_needleman_wunsch(
        sequence1,
        sequence2
    )

    print("\nGPU Needleman-Wunsch Result")
    print("Sequence 1:", result[0])
    print("Sequence 2:", result[1])
    print("Alignment Score:", result[2])
    print("\nGPU computation completed!")

