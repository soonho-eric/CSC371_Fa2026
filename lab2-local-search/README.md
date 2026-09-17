# Lab 2: Local Search

Hill climbing, sideways moves, random restarts, and simulated annealing on
n-queens and the travelling salesperson problem.


## Setup

1. Open **Miniforge Prompt** (Windows) or a terminal (macOS or Linux).

2. Activate the course environment:

   ```
   conda activate csc371
   ```

3. Install this lab's package:

   ```
   conda install -c conda-forge pandas "python=3.12"
   ```

  When it asks whether to proceed, type `y` and press Enter.

4. Copy this lab folder from the course directory to your own:

```
cp -r path/to/CSC371_Fa2026/lab2-local-search path/to/My_CSC371/
```

Then navigate to your lab2 folder and check environment:

   ```
   cd path/to/My_CSC371/lab2-local-search
   python check_environment.py
   ```

   You are looking for this last line:

   ```
   ✅ Environment ready for Lab 2 (Python 3.12.x)
   ```

   If you see anything else, read the message it prints — it names the fix —
   and then see Troubleshooting below.

5. With the course environment still active, start JupyterLab:

   ```
   jupyter lab
   ```

   Open `lab2_local_search.ipynb` and run the first cell to make sure the notebook is running the correct Python version.

---

## What is in this folder

```
lab2_local_search.ipynb   the core lab exercises
lab2_extensions.ipynb     additional practice (will be made available Friday)
check_environment.py      the setup check
lab2kit/                  the code used in the lab. You don't need to actually work with these files.
  problems.py             the NQueens and TSP classes
  experiments.py          running algorithms over many seeds
  viz.py                  the figures
  checks.py               the check functions
  results.py              the results schema and CSV export
  predictions.py          recording and revealing predictions
```

You are welcome to read anything in `lab2kit`. Reading `cost()` in
`problems.py` is a good way to see exactly how budget is counted in this lab.
