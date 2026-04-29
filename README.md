# Theory of Computation - Practice 4: Use of Regular Expressions and DFA to RE Conversion

## About The Project

This repository contains the software extension developed for Practice 4 of the Theory of Computation course at ESCOM. 
The project extends the interactive software developed in previous practices to implement the algorithmic conversion of Deterministic Finite Automata (DFA) to Regular Expressions (RE). 
Additionally, it explores the theoretical and practical applications of regular expressions for data validation

## Authors

* Angel Heron Garcia Osornio
* Alan Gabriel Ramírez Nolasco

## Core Features

* **DFA to RE Conversion:** Implements the state elimination algorithm, displaying the process interactively step-by-step until generating a clear and readable Regular Expression.
* **JFLAP Integration:** Includes functionality to import, parse, and validate automata files (`.jff`) created in JFLAP.
* **Practical Regex Validators:** Applies regular expressions to solve practical problems , featuring validators for Email addresses, National Phone Numbers, and Secure Passwords.
* **Equivalent DFA Visualization:** Allows users to understand the underlying logic of the regular expressions by displaying their equivalent DFA structure.
* **Core Automata Engine (Legacy):** Maintains full backward compatibility with NFA/NFA-λ Simulation, Subset Construction (NFA to DFA), Hopcroft's Minimization, and Batch Testing.

## Getting Started

### Prerequisites

To run this application locally, you will need **Python 3.x** installed on your system. The graphical user interface and internal parsing are built using `tkinter`, `xml.etree.ElementTree`, and `re`, which are native libraries included in standard Python distributions. No external installations via `pip` are required.

### Execution Instructions

1. Clone the repository to your local machine:
```bash
git clone [https://github.com/alaNN13/PR-CTICA-4---TEOR-A-DE-LA-COMPUTACI-N.git](https://github.com/alaNN13/PR-CTICA-4---TEOR-A-DE-LA-COMPUTACI-N.git)

2. Navigate to the project directory and execute the main file:

python mainp4.py
