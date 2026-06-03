@echo off
echo Running sorting benchmark in C, Java, and Python...

echo.
echo [1/3] C benchmark
cd c
gcc sorting_benchmark.c -O2 -o sorting_benchmark.exe
if errorlevel 1 goto error
sorting_benchmark.exe
cd ..

echo.
echo [2/3] Java benchmark
cd java
javac SortingBenchmark.java
if errorlevel 1 goto error
java SortingBenchmark
cd ..

echo.
echo [3/3] Python benchmark
cd python
python sorting_benchmark.py
cd ..

echo.
echo Done. Check the results folder for CSV files.
goto end

:error
echo A compilation or execution error occurred. Please check that GCC, Java JDK, and Python are installed.
cd ..

:end
pause
