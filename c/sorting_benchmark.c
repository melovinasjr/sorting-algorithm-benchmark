/*
Sorting Algorithm Benchmark - C Version
Compile on Windows using MinGW:
    gcc sorting_benchmark.c -O2 -o sorting_benchmark.exe
Run:
    sorting_benchmark.exe
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

#define REPEATS 5
#define MAX_VALUE 1000000
#define SAMPLE 20

typedef void (*SortFunc)(int*, int);

int is_sorted(int *a, int n) {
    for (int i = 0; i < n - 1; i++) if (a[i] > a[i+1]) return 0;
    return 1;
}

void fill_random(int *a, int n, unsigned int seed) {
    srand(seed);
    for (int i = 0; i < n; i++) a[i] = rand() % (MAX_VALUE + 1);
}

void bubble_sort(int *a, int n) {
    for (int end = n - 1; end > 0; end--)
        for (int i = 0; i < end; i++)
            if (a[i] > a[i+1]) { int t = a[i]; a[i] = a[i+1]; a[i+1] = t; }
}

void improved_bubble_sort(int *a, int n) {
    for (int end = n - 1; end > 0; end--) {
        int no_swap = 1;
        for (int i = 0; i < end; i++) {
            if (a[i] > a[i+1]) { int t = a[i]; a[i] = a[i+1]; a[i+1] = t; no_swap = 0; }
        }
        if (no_swap) break;
    }
}

void selection_sort(int *a, int n) {
    for (int i = 0; i < n - 1; i++) {
        int min_idx = i;
        for (int j = i + 1; j < n; j++) if (a[j] < a[min_idx]) min_idx = j;
        if (min_idx != i) { int t = a[i]; a[i] = a[min_idx]; a[min_idx] = t; }
    }
}

void insertion_sort(int *a, int n) {
    for (int i = 1; i < n; i++) {
        int key = a[i];
        int j = i - 1;
        while (j >= 0 && a[j] > key) { a[j+1] = a[j]; j--; }
        a[j+1] = key;
    }
}

void shell_sort(int *a, int n) {
    for (int gap = n / 2; gap > 0; gap /= 2) {
        for (int i = gap; i < n; i++) {
            int temp = a[i];
            int j = i;
            while (j >= gap && a[j-gap] > temp) { a[j] = a[j-gap]; j -= gap; }
            a[j] = temp;
        }
    }
}

void sift_down(int *a, int start, int end) {
    int root = start;
    while (1) {
        int child = 2 * root + 1;
        if (child > end) break;
        if (child + 1 <= end && a[child] < a[child+1]) child++;
        if (a[root] < a[child]) { int t = a[root]; a[root] = a[child]; a[child] = t; root = child; }
        else break;
    }
}

void heap_sort(int *a, int n) {
    for (int start = n / 2 - 1; start >= 0; start--) sift_down(a, start, n - 1);
    for (int end = n - 1; end > 0; end--) { int t = a[0]; a[0] = a[end]; a[end] = t; sift_down(a, 0, end - 1); }
}

void merge_sort_recursive(int *a, int *temp, int left, int right) {
    if (right - left <= 1) return;
    int mid = left + (right - left) / 2;
    merge_sort_recursive(a, temp, left, mid);
    merge_sort_recursive(a, temp, mid, right);
    int i = left, j = mid, k = left;
    while (i < mid && j < right) temp[k++] = (a[i] <= a[j]) ? a[i++] : a[j++];
    while (i < mid) temp[k++] = a[i++];
    while (j < right) temp[k++] = a[j++];
    for (i = left; i < right; i++) a[i] = temp[i];
}

void merge_sort(int *a, int n) {
    int *temp = (int*)malloc(sizeof(int) * n);
    if (!temp) return;
    merge_sort_recursive(a, temp, 0, n);
    free(temp);
}

int partition_q(int *a, int low, int high) {
    int pivot = a[(low + high) / 2];
    int i = low, j = high;
    while (i <= j) {
        while (a[i] < pivot) i++;
        while (a[j] > pivot) j--;
        if (i <= j) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; j--; }
    }
    return i;
}

void quick_sort_range(int *a, int low, int high) {
    if (low >= high) return;
    int idx = partition_q(a, low, high);
    if (low < idx - 1) quick_sort_range(a, low, idx - 1);
    if (idx < high) quick_sort_range(a, idx, high);
}

void quick_sort(int *a, int n) { quick_sort_range(a, 0, n - 1); }

void bucket_sort(int *a, int n) {
    int *count = (int*)calloc(MAX_VALUE + 1, sizeof(int));
    if (!count) return;
    for (int i = 0; i < n; i++) count[a[i]]++;
    int idx = 0;
    for (int v = 0; v <= MAX_VALUE; v++) while (count[v]--) a[idx++] = v;
    free(count);
}

int skip_case(const char *name, int n) {
    if ((strcmp(name, "Bubble Sort") == 0 || strcmp(name, "Improved Bubble Sort") == 0 ||
         strcmp(name, "Selection Sort") == 0 || strcmp(name, "Insertion Sort") == 0) && n > 10000) return 1;
    return 0;
}

void print_array_sample(FILE *f, int *a, int n) {
    int limit = n < SAMPLE ? n : SAMPLE;
    fprintf(f, "[");
    for (int i = 0; i < limit; i++) fprintf(f, "%d%s", a[i], (i == limit - 1 ? "" : " "));
    fprintf(f, "]");
}

int main() {
    int sizes[] = {1000, 10000, 100000, 1000000};
    const char *names[] = {"Bubble Sort", "Improved Bubble Sort", "Selection Sort", "Heap Sort", "Insertion Sort", "Shell Sort", "Merge Sort", "Quick Sort", "Bucket Sort"};
    SortFunc funcs[] = {bubble_sort, improved_bubble_sort, selection_sort, heap_sort, insertion_sort, shell_sort, merge_sort, quick_sort, bucket_sort};
    int alg_count = 9;

    FILE *results = fopen("../results/c_results.csv", "w");
    FILE *samples = fopen("../results/c_before_after_samples.csv", "w");
    fprintf(results, "language,algorithm,data_size,runs,average_seconds,stdev_seconds,status,verified_sorted\n");
    fprintf(samples, "language,algorithm,data_size,before_first_20,after_first_20\n");

    for (int s = 0; s < 4; s++) {
        int n = sizes[s];
        int *base = (int*)malloc(sizeof(int) * n);
        int *a = (int*)malloc(sizeof(int) * n);
        if (!base || !a) { fprintf(results, "C,ALL,%d,,,,OUT_OF_SPACE,No\n", n); continue; }
        fill_random(base, n, 20260603u + n);
        for (int alg = 0; alg < alg_count; alg++) {
            if (skip_case(names[alg], n)) {
                fprintf(results, "C,%s,%d,,,,TIMEOUT_ESTIMATED_GT_10_MIN_OR_IMPRACTICAL,Not executed\n", names[alg], n);
                continue;
            }
            double times[REPEATS]; int verified = 1;
            int after_written = 0;
            for (int r = 0; r < REPEATS; r++) {
                memcpy(a, base, sizeof(int) * n);
                clock_t start = clock();
                funcs[alg](a, n);
                clock_t end = clock();
                times[r] = (double)(end - start) / CLOCKS_PER_SEC;
                verified = verified && is_sorted(a, n);
                if (!after_written) {
                    fprintf(samples, "C,%s,%d,", names[alg], n);
                    print_array_sample(samples, base, n);
                    fprintf(samples, ",");
                    print_array_sample(samples, a, n);
                    fprintf(samples, "\n");
                    after_written = 1;
                }
            }
            double sum = 0; for (int r = 0; r < REPEATS; r++) sum += times[r];
            double avg = sum / REPEATS;
            double var = 0; for (int r = 0; r < REPEATS; r++) var += (times[r] - avg) * (times[r] - avg);
            double stdev = sqrt(var / (REPEATS - 1));
            fprintf(results, "C,%s,%d,\"", names[alg], n);
            for (int r = 0; r < REPEATS; r++) fprintf(results, "%.6f%s", times[r], r == REPEATS - 1 ? "" : ";");
            fprintf(results, "\",%.6f,%.6f,OK,%s\n", avg, stdev, verified ? "True" : "False");
        }
        free(base); free(a);
    }
    fclose(results); fclose(samples);
    return 0;
}
