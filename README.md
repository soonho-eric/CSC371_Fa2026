# CSC371_Fa2026
Materials for CSC 371: Artificial Intelligence and Applied Machine Learning at Ripon College


## Getting Started!

Welcome to CSC 371! In this class we will learn AI and ML by writing and building.

## Day 1

Install Git and clone this repository using [this guide](docs/git_setup.md).

Then, set up your own private github repository.
Use the following lines to create some directories:

```bash
mkdir journal
mkdir lab
mkdir exercises
```

We will primarily use the Python programming language. We will also use Anaconda (specifically mini-forge), a package management system for Python.
[Install miniforge](https://github.com/conda-forge/miniforge) using their instructions for your system.
(If you already have miniforge, miniconda, or conda installed, go ahead and use that.)
Use the following lines in your terminal to set up a conda environment and install some basic packages.

```bash
conda create -n csc371 python=3.12
conda activate csc371
conda install numpy scipy matplotlib jupyterlab
```

Create a Jupyter notebook titled "Day01.ipynb". Create a 'Hello World!' script and play around with the environment.

In your terminal, run
```bash
git status
git add .
git status
git commit -m 'Day 1'
git push
```
