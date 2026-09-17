"""Check that this Python has everything Lab 2 needs.

Run it either way:

    python check_environment.py          # from a terminal, in the lab folder
    %run check_environment.py            # from the notebook's first cell

Only the standard library is used to decide anything, so this script can
still explain itself when the packages it is looking for are missing.
"""

import importlib
import sys

REQUIRED_PYTHON = (3, 12)
REQUIRED_PACKAGES = ["numpy", "scipy", "matplotlib", "pandas"]

INSTALL_COMMAND = 'conda install -c conda-forge pandas "python=3.12"'
ENV_NAME = "csc371"


class StopExecution(Exception):
    """Ends a notebook cell quietly, without printing a traceback."""

    def _render_traceback_(self):
        return []


def _in_notebook():
    """True when this script is being run from inside an IPython kernel."""
    ipython = sys.modules.get("IPython")
    return bool(ipython and ipython.get_ipython() is not None)


def _check_python():
    """Return a list of problems with the running interpreter."""
    found = sys.version_info[:2]
    print(f"Python {'.'.join(str(part) for part in sys.version_info[:3])}")
    print(f"interpreter: {sys.executable}")
    if found == REQUIRED_PYTHON:
        return []
    return [
        f"This is Python {found[0]}.{found[1]}, but Lab 2 needs "
        f"{REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}.\n"
        f"  Most likely cause: this notebook or terminal is using a different "
        f"environment than the course one.\n"
        f"  Look at the interpreter path above: it should end in "
        f"envs/{ENV_NAME}/bin/python (macOS or Linux) or "
        f"envs\\{ENV_NAME}\\python.exe (Windows).\n"
        f"  Fix: close JupyterLab, run  conda activate {ENV_NAME}  and start it "
        f"again with  jupyter lab"
    ]


def _check_packages():
    """Import each required package in turn and report what is missing."""
    problems = []
    for name in REQUIRED_PACKAGES:
        try:
            module = importlib.import_module(name)
        except ImportError as error:
            problems.append(
                f"{name} could not be imported ({error}).\n"
                f"  Most likely cause: {name} is not installed in this "
                f"environment, or JupyterLab was started from a different one.\n"
                f"  Fix: conda activate {ENV_NAME}\n"
                f"       {INSTALL_COMMAND}"
            )
        else:
            print(f"  {name} {getattr(module, '__version__', 'version unknown')}")
    return problems


def main():
    """Run every check, print a report, and return the number of problems."""
    problems = _check_python()
    problems += _check_packages()

    if not problems:
        version = ".".join(str(part) for part in sys.version_info[:3])
        print(f"✅ Environment ready for Lab 2 (Python {version})")
        return 0

    print()
    print(f"❌ Setup is not finished yet — {len(problems)} problem(s) to fix:")
    for index, problem in enumerate(problems, start=1):
        print(f"\n{index}. {problem}")
    print(
        "\nThe 'Setup' section of README.md walks through this step by step."
    )
    return len(problems)


if __name__ == "__main__":
    failures = main()
    if failures:
        if _in_notebook():
            print("\nStopping here so the cells below do not fail confusingly.")
            raise StopExecution
        sys.exit(1)
