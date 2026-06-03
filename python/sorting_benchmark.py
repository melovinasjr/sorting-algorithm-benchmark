"""
Sorting Algorithm Benchmark - Python Version
Lab requirements:
- Algorithms: bubble, improved bubble, selection, heap, insertion, shell, merge, quick, bucket/counting sort.
- Data sizes: 1,000; 10,000; 100,000; 1,000,000 random integers.
- Integer range: 0 to 1,000,000; duplicates allowed.
- Each algorithm is executed 5 times per data size; the average execution time is recorded.
- Very slow cases are logged as TIMEOUT_ESTIMATED instead of waiting more than 10 minutes.

Run on Windows:
    python sorting_benchmark.py
"""

import csv
import random
import time
import platform
import statistics
from pathlib import Path

REPEATS = 5
DATA_SIZES = [1000, 10000, 100000, 1000000]
MAX_VALUE = 1_000_000
SEED = 20260603
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "results"
OUTPUT_DIR.mkdir(exist_ok=True)

# Safety rule: the lab says to log algorithms that take too long (>10 min).
# These algorithms are O(n^2), so 100,000 and 1,000,000 random values are normally impractical.
SKIP_LIMITS = {
    "Bubble Sort": 10000,
    "Improved Bubble Sort": 10000,
    "Selection Sort": 10000,
    "Insertion Sort": 10000,
}


def bubble_sort(a):
    n = len(a)
    for end in range(n - 1, 0, -1):
        for i in range(end):
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]


def improved_bubble_sort(a):
    n = len(a)
    for end in range(n - 1, 0, -1):
        no_swap = True
        for i in range(end):
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
                no_swap = False
        if no_swap:
            break


def selection_sort(a):
    n = len(a)
    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            if a[j] < a[min_idx]:
                min_idx = j
        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]


def insertion_sort(a):
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key


def shell_sort(a):
    n = len(a)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = a[i]
            j = i
            while j >= gap and a[j - gap] > temp:
                a[j] = a[j - gap]
                j -= gap
            a[j] = temp
        gap //= 2


def heap_sort(a):
    n = len(a)

    def sift_down(start, end):
        root = start
        while True:
            child = 2 * root + 1
            if child > end:
                break
            if child + 1 <= end and a[child] < a[child + 1]:
                child += 1
            if a[root] < a[child]:
                a[root], a[child] = a[child], a[root]
                root = child
            else:
                break

    for start in range(n // 2 - 1, -1, -1):
        sift_down(start, n - 1)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        sift_down(0, end - 1)


def merge_sort(a):
    n = len(a)
    width = 1
    temp = [0] * n
    src, dst = a, temp
    while width < n:
        for left in range(0, n, 2 * width):
            mid = min(left + width, n)
            right = min(left + 2 * width, n)
            i, j, k = left, mid, left
            while i < mid and j < right:
                if src[i] <= src[j]:
                    dst[k] = src[i]
                    i += 1
                else:
                    dst[k] = src[j]
                    j += 1
                k += 1
            while i < mid:
                dst[k] = src[i]
                i += 1
                k += 1
            while j < right:
                dst[k] = src[j]
                j += 1
                k += 1
        src, dst = dst, src
        width *= 2
    if src is not a:
        a[:] = src[:]


def quick_sort(a):
    # Iterative quicksort with insertion sort cutoff to avoid recursion depth problems.
    def partition(lo, hi):
        mid = (lo + hi) // 2
        # median-of-three
        if a[mid] < a[lo]:
            a[lo], a[mid] = a[mid], a[lo]
        if a[hi] < a[lo]:
            a[lo], a[hi] = a[hi], a[lo]
        if a[hi] < a[mid]:
            a[mid], a[hi] = a[hi], a[mid]
        pivot = a[mid]
        i, j = lo, hi
        while True:
            while a[i] < pivot:
                i += 1
            while a[j] > pivot:
                j -= 1
            if i >= j:
                return j
            a[i], a[j] = a[j], a[i]
            i += 1
            j -= 1

    stack = [(0, len(a) - 1)]
    while stack:
        lo, hi = stack.pop()
        while lo < hi:
            if hi - lo < 24:
                for i in range(lo + 1, hi + 1):
                    key = a[i]
                    j = i - 1
                    while j >= lo and a[j] > key:
                        a[j + 1] = a[j]
                        j -= 1
                    a[j + 1] = key
                break
            p = partition(lo, hi)
            # Sort smaller section first to keep stack small.
            if p - lo < hi - (p + 1):
                stack.append((p + 1, hi))
                hi = p
            else:
                stack.append((lo, p))
                lo = p + 1


def bucket_sort(a):
    # Since values are fixed in 0..1,000,000, bucket sort is implemented as counting buckets.
    counts = [0] * (MAX_VALUE + 1)
    for x in a:
        counts[x] += 1
    idx = 0
    for value, count in enumerate(counts):
        for _ in range(count):
            a[idx] = value
            idx += 1


def is_sorted(a):
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


def benchmark():
    algorithms = [
        ("Bubble Sort", bubble_sort),
        ("Improved Bubble Sort", improved_bubble_sort),
        ("Selection Sort", selection_sort),
        ("Heap Sort", heap_sort),
        ("Insertion Sort", insertion_sort),
        ("Shell Sort", shell_sort),
        ("Merge Sort", merge_sort),
        ("Quick Sort", quick_sort),
        ("Bucket Sort", bucket_sort),
    ]

    result_rows = []
    sample_rows = []

    for n in DATA_SIZES:
        random.seed(SEED + n)
        base_data = [random.randint(0, MAX_VALUE) for _ in range(n)]
        for alg_name, func in algorithms:
            if n > SKIP_LIMITS.get(alg_name, 10**12):
                result_rows.append({
                    "language": "Python",
                    "algorithm": alg_name,
                    "data_size": n,
                    "runs": "",
                    "average_seconds": "",
                    "stdev_seconds": "",
                    "status": "TIMEOUT_ESTIMATED_GT_10_MIN_OR_IMPRACTICAL",
                    "verified_sorted": "Not executed",
                })
                continue

            times = []
            verified = True
            before_sample = base_data[:20]
            after_sample = None
            for _ in range(REPEATS):
                a = base_data.copy()
                start = time.perf_counter()
                func(a)
                elapsed = time.perf_counter() - start
                times.append(elapsed)
                verified = verified and is_sorted(a)
                if after_sample is None:
                    after_sample = a[:20]
            result_rows.append({
                "language": "Python",
                "algorithm": alg_name,
                "data_size": n,
                "runs": ";".join(f"{t:.6f}" for t in times),
                "average_seconds": f"{statistics.mean(times):.6f}",
                "stdev_seconds": f"{statistics.stdev(times) if len(times) > 1 else 0:.6f}",
                "status": "OK",
                "verified_sorted": str(verified),
            })
            sample_rows.append({
                "language": "Python",
                "algorithm": alg_name,
                "data_size": n,
                "before_first_20": before_sample,
                "after_first_20": after_sample,
            })

    with open(OUTPUT_DIR / "python_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(result_rows[0].keys()))
        writer.writeheader()
        writer.writerows(result_rows)

    with open(OUTPUT_DIR / "python_before_after_samples.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(sample_rows[0].keys()))
        writer.writeheader()
        writer.writerows(sample_rows)

    with open(OUTPUT_DIR / "python_environment.txt", "w", encoding="utf-8") as f:
        f.write(f"Python version: {platform.python_version()}\n")
        f.write(f"Platform: {platform.platform()}\n")
        f.write(f"Repeats: {REPEATS}\n")
        f.write(f"Data sizes: {DATA_SIZES}\n")
        f.write(f"Random range: 0..{MAX_VALUE}\n")
        f.write(f"Seed: {SEED}\n")

    print("Benchmark completed. Results saved in:", OUTPUT_DIR)


if __name__ == "__main__":
    benchmark()
