# Numpy Tutorial: First Steps in Data Science

This folder contains the sample code for the [NumPy Tutorial](https://realpython.com/numpy-tutorial/) by @rpalo.

## Installing

First, you will need to have the dependencies installed:

```shell
$ python -m pip install -r requirements.txt
```

## Usage

These examples all make use of the [Jupyter Notebook](https://jupyter-notebook.readthedocs.io/en/stable/). To run the examples, make sure the correct virtual environment is active (you may have to deactivate and reactivate after installing requirements), and run:

```shell
$ jupyter notebook
```

You should see listings for each of the example files.  You can open them up and run them cell by cell to see how they perform.  Feel free to make small changes to the code to see how those affect things.

## Complexity and Performance Analysis

### Grade Curving Algorithm (`curve_grades`)
- **Input size variable ($N$)**: Total number of grade elements in the dataset.
- **Theoretical Time Complexity**: $\mathcal{O}(N)$ worst-case and average-case. The calculation computes the mean with one pass over the array ($\mathcal{O}(N)$), adds a scalar offset to all elements ($\mathcal{O}(N)$), and clips the bounded result ($\mathcal{O}(N)$).
- **Theoretical Space Complexity**: $\mathcal{O}(N)$ auxiliary space for returning the new adjusted array.
- **Empirical Observations**: Verified with fixed pseudo-random seeds across sizes $N=100$, $N=1000$, and $N=10000$ (5 repetitions each, reporting median and range). Operation counts scale strictly linearly with $N$ ($\mathcal{O}(N)$).
