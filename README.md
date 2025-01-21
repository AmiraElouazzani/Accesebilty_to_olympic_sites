# Minimum Dominating Station Set for Bipartite Graphs with Distance Constraints (MDSS-OS)

## Problem Overview

This repository implements a solution to the **Minimum Dominating Station Set for Bipartite Graphs with Distance Constraints (MDSS-OS)** problem. The problem focuses on identifying the smallest set of **stations** that can "dominate" or cover all **Olympic sites**, under certain walking distance.

### Problem Input:

1. **Bipartite Graph**: 
   - The input is a bipartite graph G = (V, E), where:
     - V = S ∪ O
     - S is the set of **stations**.
     - O is the set of **Olympic sites**.
   - There exists an edge e = (s, o) ∈ E between a station s ∈ S and an Olympic site o ∈ O if and only if the **walking distance** between them is less than or equal to a predefined distance threshold d_max.

2. **walking Distance Constraint**:
   - For every pair of nodes (station s and Olympic site o), the distance between them is computed using walking distance.
   - An edge is created between s and o if the walking distance between them is less than or equal to x.

### Objective:

- **Goal**: Find the smallest subset A ⊆ S (a subset of stations) such that every Olympic site o ∈ O is **dominated**.
  - An Olympic site o ∈ O is considered dominated if it is **adjacent** to at least one station s ∈ A.
                    ∀o∈O, ∃s∈A such that (s,o)∈E

### Key Characteristics:

- **Bipartite Graph Structure**: The graph consists of two disjoint sets of vertices, stations (S) and Olympic sites (O), with edges only between these two sets.
- **Distance Threshold**: Only stations and Olympic sites within a certain walking distance x are connected by edges.
- **Dominating Set**: The goal is to find a **minimum dominating set** of stations that covers all Olympic sites.


# Execution 
To execute the main program:

```
python3 main.py
```

from the project root.

To execute a third-party program that is not located at the root:

```
python3 -m path.to.my.file
```

(no .py extension), don't forget the dots for relative imports.

# Benchmarks

Some Benchmarks are implemented in ```src/Benchmark.py```, but some bugs remain.