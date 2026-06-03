/*
Sorting Algorithm Benchmark - Java Version
Compile on Windows:
    javac SortingBenchmark.java
Run:
    java SortingBenchmark
*/
import java.io.*;
import java.util.*;

public class SortingBenchmark {
    static final int REPEATS = 5;
    static final int[] DATA_SIZES = {1000, 10000, 100000, 1000000};
    static final int MAX_VALUE = 1_000_000;
    static final long SEED = 20260603L;

    interface Sorter { void sort(int[] a); }

    static void bubbleSort(int[] a) {
        for (int end = a.length - 1; end > 0; end--)
            for (int i = 0; i < end; i++)
                if (a[i] > a[i+1]) { int t = a[i]; a[i] = a[i+1]; a[i+1] = t; }
    }

    static void improvedBubbleSort(int[] a) {
        for (int end = a.length - 1; end > 0; end--) {
            boolean noSwap = true;
            for (int i = 0; i < end; i++) {
                if (a[i] > a[i+1]) { int t = a[i]; a[i] = a[i+1]; a[i+1] = t; noSwap = false; }
            }
            if (noSwap) break;
        }
    }

    static void selectionSort(int[] a) {
        for (int i = 0; i < a.length - 1; i++) {
            int min = i;
            for (int j = i + 1; j < a.length; j++) if (a[j] < a[min]) min = j;
            if (min != i) { int t = a[i]; a[i] = a[min]; a[min] = t; }
        }
    }

    static void insertionSort(int[] a) {
        for (int i = 1; i < a.length; i++) {
            int key = a[i], j = i - 1;
            while (j >= 0 && a[j] > key) { a[j + 1] = a[j]; j--; }
            a[j + 1] = key;
        }
    }

    static void shellSort(int[] a) {
        for (int gap = a.length / 2; gap > 0; gap /= 2) {
            for (int i = gap; i < a.length; i++) {
                int temp = a[i], j = i;
                while (j >= gap && a[j-gap] > temp) { a[j] = a[j-gap]; j -= gap; }
                a[j] = temp;
            }
        }
    }

    static void heapSort(int[] a) {
        for (int start = a.length / 2 - 1; start >= 0; start--) siftDown(a, start, a.length - 1);
        for (int end = a.length - 1; end > 0; end--) {
            int t = a[0]; a[0] = a[end]; a[end] = t;
            siftDown(a, 0, end - 1);
        }
    }

    static void siftDown(int[] a, int start, int end) {
        int root = start;
        while (true) {
            int child = 2 * root + 1;
            if (child > end) break;
            if (child + 1 <= end && a[child] < a[child + 1]) child++;
            if (a[root] < a[child]) { int t = a[root]; a[root] = a[child]; a[child] = t; root = child; }
            else break;
        }
    }

    static void mergeSort(int[] a) {
        int[] temp = new int[a.length];
        mergeSortRec(a, temp, 0, a.length);
    }
    static void mergeSortRec(int[] a, int[] temp, int left, int right) {
        if (right - left <= 1) return;
        int mid = left + (right - left) / 2;
        mergeSortRec(a, temp, left, mid);
        mergeSortRec(a, temp, mid, right);
        int i = left, j = mid, k = left;
        while (i < mid && j < right) temp[k++] = (a[i] <= a[j]) ? a[i++] : a[j++];
        while (i < mid) temp[k++] = a[i++];
        while (j < right) temp[k++] = a[j++];
        for (i = left; i < right; i++) a[i] = temp[i];
    }

    static void quickSort(int[] a) { quickSortRange(a, 0, a.length - 1); }
    static void quickSortRange(int[] a, int low, int high) {
        if (low >= high) return;
        int i = low, j = high, pivot = a[(low + high) / 2];
        while (i <= j) {
            while (a[i] < pivot) i++;
            while (a[j] > pivot) j--;
            if (i <= j) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; j--; }
        }
        if (low < j) quickSortRange(a, low, j);
        if (i < high) quickSortRange(a, i, high);
    }

    static void bucketSort(int[] a) {
        int[] count = new int[MAX_VALUE + 1];
        for (int x : a) count[x]++;
        int idx = 0;
        for (int v = 0; v <= MAX_VALUE; v++) while (count[v]-- > 0) a[idx++] = v;
    }

    static boolean isSorted(int[] a) {
        for (int i = 0; i < a.length - 1; i++) if (a[i] > a[i+1]) return false;
        return true;
    }

    static boolean skipCase(String name, int n) {
        return (name.equals("Bubble Sort") || name.equals("Improved Bubble Sort") || name.equals("Selection Sort") || name.equals("Insertion Sort")) && n > 10000;
    }

    static String sample(int[] a) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < Math.min(20, a.length); i++) {
            if (i > 0) sb.append(' ');
            sb.append(a[i]);
        }
        return sb.append(']').toString();
    }

    public static void main(String[] args) throws Exception {
        new File("../results").mkdirs();
        PrintWriter results = new PrintWriter(new FileWriter("../results/java_results.csv"));
        PrintWriter samples = new PrintWriter(new FileWriter("../results/java_before_after_samples.csv"));
        results.println("language,algorithm,data_size,runs,average_seconds,stdev_seconds,status,verified_sorted");
        samples.println("language,algorithm,data_size,before_first_20,after_first_20");

        String[] names = {"Bubble Sort", "Improved Bubble Sort", "Selection Sort", "Heap Sort", "Insertion Sort", "Shell Sort", "Merge Sort", "Quick Sort", "Bucket Sort"};
        Sorter[] funcs = {SortingBenchmark::bubbleSort, SortingBenchmark::improvedBubbleSort, SortingBenchmark::selectionSort, SortingBenchmark::heapSort, SortingBenchmark::insertionSort, SortingBenchmark::shellSort, SortingBenchmark::mergeSort, SortingBenchmark::quickSort, SortingBenchmark::bucketSort};

        for (int n : DATA_SIZES) {
            Random rng = new Random(SEED + n);
            int[] base = new int[n];
            for (int i = 0; i < n; i++) base[i] = rng.nextInt(MAX_VALUE + 1);

            for (int alg = 0; alg < names.length; alg++) {
                if (skipCase(names[alg], n)) {
                    results.printf("Java,%s,%d,,,,TIMEOUT_ESTIMATED_GT_10_MIN_OR_IMPRACTICAL,Not executed%n", names[alg], n);
                    continue;
                }
                double[] times = new double[REPEATS];
                boolean verified = true;
                int[] firstAfter = null;
                for (int r = 0; r < REPEATS; r++) {
                    int[] a = Arrays.copyOf(base, base.length);
                    long start = System.nanoTime();
                    funcs[alg].sort(a);
                    long end = System.nanoTime();
                    times[r] = (end - start) / 1e9;
                    verified &= isSorted(a);
                    if (firstAfter == null) firstAfter = Arrays.copyOf(a, Math.min(20, a.length));
                }
                double avg = 0; for (double t : times) avg += t; avg /= REPEATS;
                double var = 0; for (double t : times) var += (t - avg) * (t - avg); double sd = Math.sqrt(var / (REPEATS - 1));
                StringBuilder runs = new StringBuilder();
                for (int r = 0; r < times.length; r++) { if (r > 0) runs.append(';'); runs.append(String.format(Locale.US, "%.6f", times[r])); }
                results.printf(Locale.US, "Java,%s,%d,\"%s\",%.6f,%.6f,OK,%s%n", names[alg], n, runs, avg, sd, verified);
                samples.printf("Java,%s,%d,%s,%s%n", names[alg], n, sample(base), sample(firstAfter));
            }
        }
        results.close();
        samples.close();
    }
}
