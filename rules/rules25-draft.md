# 20th International Satisfiability Modulo Theories Competition (SMT-COMP 2025): Rules and Procedures

## Communication

Interested parties should subscribe to the SMT-COMP mailing list. Important news and clarifications will be announced there.

- SMT-COMP mailing list: [smt-comp@googlegroups.com](mailto:smt-comp@googlegroups.com)
- Sign-up site for the mailing list: [https://groups.google.com/g/smt-comp](https://groups.google.com/g/smt-comp)
- Competition website: [http://www.smtcomp.org](http://www.smtcomp.org)

## Important Dates

### 2025 Deadlines:

- **April 12**: Deadline for new benchmark contributions.
- **May 31**: Final versions of competition tools and benchmark libraries are frozen.
- **June 13**: Deadline for first versions of solvers (all tracks) and track/division entry information.
- **June 27**: Deadline for final versions of solvers, including system descriptions.
- **June 30**: Opening value of NYSE Composite Index used for random seed.
- **August 10-11**: SMT Workshop; end of competition, presentation of results.

## Introduction

The annual SMT-COMP aims to advance SMT solver implementations on benchmarks of practical interest. The competition encourages researchers to submit new benchmarks and solvers to foster innovation in automated SMT problem-solving.

SMT-COMP 2025 is part of the **SMT Workshop 2025**, affiliated with **SAT 2025**:
- SMT Workshop: [http://smt-workshop.cs.uiowa.edu/2025/](http://smt-workshop.cs.uiowa.edu/2025/)
- SAT 2025: [https://satisfiability.org/SAT25/](https://satisfiability.org/SAT25/)

### Competition Tracks:

1. **Single Query Track** (previously Main Track)
2. **Incremental Track** (previously Application Track)
3. **Unsat-Core Track**
4. **Model-Validation Track**
5. **Parallel Track**

Each track contains multiple divisions based on SMT-LIB logics.

## Entrants

### SMT Solver Categories

- **SMT Solver**: Determines satisfiability of SMT-LIB benchmark formulas.
- **Portfolio Solver**: Uses multiple solvers on the same input problem (**not allowed** in general).
- **Wrapper Tool**: Calls one or more SMT solvers to solve different subproblems (**allowed** if it does not directly call an SMT solver for the same input logic).
- **Derived Tool**: Extends an existing solver (base solver) with new features. Must acknowledge the base solver.

### Submission Requirements

- **Submission via GitHub pull request**: [https://github.com/SMT-COMP/smt-comp.github.io/tree/master/submissions](https://github.com/SMT-COMP/smt-comp.github.io/tree/master/submissions)
- **Final solver version must be uploaded to Zenodo**: [https://zenodo.org/](https://zenodo.org/)
- **System description** (1-2 pages) must be provided, explicitly acknowledging any wrapped or base solver.
- **Final version submission deadline**: **June 27, 2025**.

## Execution of Solvers

### Logistics

- **Competition Dates**: June 2025 - August 2025
- **Execution Framework**: BenchExec ([https://github.com/sosy-lab/benchexec](https://github.com/sosy-lab/benchexec))
- **Computing Environment**: SoSy-Lab BenchExec cluster and a 256-core, 2TB RAM machine for the Parallel Track.
- **Time Limit**: 20 minutes per solver/benchmark pair (except Parallel Track: 2 minutes).
- **Memory Limit**: Approx. **30GB per solver instance**.

### Input/Output Requirements

- **SMT-LIB v2.6 format**.
- **Standard Input**: Solvers read benchmark files from the command-line argument.
- **Standard Output**: Solvers return `sat`, `unsat`, or `unknown`.
- **Incremental Track**: Interaction through standard input.
- **Unsat-Core Track**: Uses `(get-unsat-core)` command.
- **Model-Validation Track**: Uses `(get-model)` command.
- **Persistent State**: Solvers may create files but cannot read them in subsequent runs.
- **Benchmark Scrambling**: Benchmark files are scrambled before execution.

## Benchmarks and Problem Divisions

### Competitive Divisions

A division is **competitive** if at least **two distinct solvers** are submitted. Non-competitive divisions will not be run.

### Benchmark Selection Process

1. **Remove inappropriate/uninteresting benchmarks**.
2. **Remove benchmarks solved by all solvers in <1s (Main Track)**.
3. **Remove benchmarks with conflicting results from past years**.
4. **Limit benchmarks per division**:
   - If **≤300**, all are selected.
   - If **301-600**, select 300.
   - If **>600**, select 50%.
5. **Random selection of benchmarks, prioritizing new ones**.
6. **Scrambling applied to avoid reliance on syntactic features**.

## Scoring

### Benchmark Scoring

Each solver receives a tuple score **`(e, n, aw, w, ac, c)`**:
- `e`: **Error score** (incorrect results count, ideally 0)
- `n`: **Correctly solved score**
- `aw`: **Actual wall-clock time**
- `w`: **Wall-clock time score** (0 if incorrect/timeout)
- `ac`: **Actual CPU time**
- `c`: **CPU time score**

### Division Scoring

- **Parallel Score**: Sum of benchmark scores.
- **Sequential Score**: Like Parallel Score, but limited to single-core execution.
- **24-Second Score**: Performance within 24s time limit.
- **Sat/Unsat Scores**: Performance on satisfiable/unsatisfiable instances only.

### Competition-Wide Recognitions

1. **Biggest Lead Ranking**: Solver with the largest gap to the second-best solver.
2. **Largest Contribution Ranking**: Solver that contributes most uniquely to virtual best solver.
3. **New Entrant Award**: New solvers that outperform existing solvers.
4. **Benchmark Contribution Award**: Recognizing benchmark contributors.

## Judging

The organizers may remove benchmarks if deemed faulty and clarify ambiguities. Authors may appeal decisions. Final decisions rest with the organizers.

## Organizers

SMT-COMP 2025 is organized under the SMT Steering Committee:

- **François Bobot** (CEA List, France)
- **David Déharbe** (CLEARSY, France)
- **Martin Jonáš** (Masaryk University, Czechia, Chair)
- **Dominik Winterer** (ETH Zurich, Switzerland)

Special thanks to **SoSy-Lab (LMU)** for providing BenchExec computing resources.

---

For the full set of rules and procedures, visit: [http://www.smtcomp.org](http://www.smtcomp.org).
