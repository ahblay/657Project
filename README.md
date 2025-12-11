# Clobber Solver

## Setup

You will need a compiled binary of **SEGClobber**. This project contains the pre-compiled SEGClobber binary for Mac.

### On Mac

1. Navigate to the main directory.
2. Run:

   ```bash
   ./startup.sh
   export SEGCLOBBER_BINARY=$(pwd)/bin/segclobber
   ```

   This will save the path to the pre-compiled SEGClobber binary as an environment variable.

### On PC

1. Navigate to the main directory.
2. Run:

   ```bash
   ./startup.sh compile
   export SEGCLOBBER_BINARY=$(pwd)/solver/src/segclobber
   ```

   The `compile` flag will clone and compile the SEGClobber binary and set the path to it as an environment variable.

### Troubleshooting

If you encounter any errors with SEGClobber on Mac, run ```./startup.sh compile``` to clone and compile the binary locally. Then manually set the path to the binary with ```export SEGCLOBBER_BINARY=$(pwd)/solver/src/segclobber```.

---

## Running the Solver

The solver is executed using `python3 run.py` with the following flags:

* `--state` : The starting position to solve, given as a string `"{p}_{s}"`, where `p` and `s` are both xo-strings, and `_` represents a repeating pattern.
* `--q` : The repeating pattern represented by `_`.
* `--prefixes` : A variable number of prefixes to prepend to the repeating pattern.
* `--suffixes` : A variable number of suffixes to append to the repeating pattern.
* `--json` : Name of the directory to store the output game tree.

### Example

```bash
python3 run.py --state xo_ --q x --prefixes xo --json example
```

This command will solve the outcome class of the game `xo(x)^n = xox...x` and write the game tree as a JSON file to `json/example/example_proof_node.json`.

> **Note:**
> If `state` contains any prefix or suffix, they must be included with the `--prefixes` and `--suffixes` flags.
> If you run without any flags, `state` is set to `_` and `q` is set to `xxo`. This will attempt to solve the game `(xxo)^n`.

---

## Simple Tests

Try running the following commands and copying the JSON output to [https://jsontree.vercel.app/](https://jsontree.vercel.app/):

1. **Test 1**

   ```bash
   python3 run.py --state o_ --q x --prefixes o --json example1
   ```

   This will solve the game `o(x)^n = ox...x`.
   **Expected outcome:** `L` (x wins)

2. **Test 2**

   ```bash
   python3 run.py --state xxo_ --q x --prefixes xxo --json example2
   ```

   This will solve the game `xxo(x)^n = xxox...x`.
   **Expected outcome:** `L` (x wins)

3. **Test 3**

   ```bash
   python3 run.py --state oox_ --q o --prefixes oox --json example3
   ```

   This will solve the game `oox(o)^n = ooxo...o`.
   **Expected outcome:** `R` (mirror of example2)

4. **Test 4**

   ```bash
   python3 run.py --state xoo_ox --q x --prefixes xoo --suffixes ox --json example4
   ```

   This will solve the game `xoo(x)^nox = xxox...xox`.
   **Expected outcome:** `N` (next player to move wins)
