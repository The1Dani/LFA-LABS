# Chomsky Normal Form (CNF)

### Course: Formal Languages & Finite Automata
### Author: Daniel Canter FAF-242

----

## Objectives:

1. Implement a method for normalizing an input grammar by the rules of CNF.
    1. The implementation needs to be encapsulated in a method with an appropriate signature (also ideally in an appropriate class/type).
    2. The implemented functionality needs executed and tested.
    3. Also, another **BONUS point** would be given if the student will make the aforementioned function to accept any grammar, not only the one from the student's variant.
## Implementation description

In this laboratory work my goal was to implement a Python program that transforms a context-free grammar into Chomsky Normal Form (CNF), while following the required sequence of simplification steps.

The implementation is written in pure Python (no third-party libraries) and uses a lean internal grammar representation:

- `VN` as a set of non-terminals
- `VT` as a set of terminals
- `S` as the start symbol
- `P` as a dictionary where each left-hand side maps to a set of right-hand side tuples

This structure keeps the code compact and automatically removes duplicate productions.

### Input and output format

The program reads a grammar from a JSON file (`grammar.json`) and prints the resulting CNF grammar as formatted JSON in the terminal.

Epsilon is represented in input as an empty list `[]`, and internally as an empty tuple `()`.

### Step 1: Elimination of epsilon productions

The function `eliminate_epsilon` computes nullable non-terminals using a fixed-point approach:

- direct nullable symbols from productions like `A -> ε`
- indirect nullable symbols where all symbols in a production are nullable

After nullable symbols are known, all valid combinations of removing nullable occurrences from productions are generated, excluding the empty result. All explicit epsilon productions are removed.

### Step 2: Elimination of renaming (unit) productions

The function `eliminate_unit` removes rules of the form `A -> B`, where both are non-terminals.

It builds a unit graph and computes unit-closure for every non-terminal. Then each non-terminal inherits only the non-unit productions reachable through that closure. This removes all renaming chains.

### Step 3: Elimination of inaccessible symbols

The function `eliminate_inaccessible` starts from the start symbol `S` and marks all non-terminals reachable through productions.

Any non-terminal and production not reachable from `S` is removed.

### Step 4: Elimination of non-productive symbols

The function `eliminate_nonproductive` computes productive non-terminals:

- a non-terminal is productive if it can derive a string of terminals
- productivity is computed with a fixed-point loop

After that, all productions containing non-productive symbols are removed, and `VN` is reduced to productive symbols only.

### Step 5: Conversion to Chomsky Normal Form

The function `to_cnf` enforces CNF production shapes:

- `A -> a`
- `A -> BC`

For productions longer than one symbol:

1. terminals in mixed right-hand sides are replaced with helper non-terminals such as `T_a -> a`
2. right-hand sides longer than 2 are binarized using fresh symbols like `N1`, `N2`, ...

After this transformation, all productions satisfy CNF requirements.

### Program flow

The script `cnf_converter.py` executes the pipeline in the required order:

1. eliminate epsilon productions
2. eliminate renaming productions
3. eliminate inaccessible symbols
4. eliminate non-productive symbols
5. convert to CNF

Finally, it prints the resulting grammar object to terminal in JSON format.

## Conclusion

In this laboratory work I implemented a lean CNF converter in Python without external libraries. The program follows the exact transformation order required by the assignment and outputs the final grammar in Chomsky Normal Form. The implementation demonstrates how formal grammar simplification steps can be automated in a practical and compact way.
