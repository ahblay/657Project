import argparse
import generator

def parse(l):
    output = set()
    for item in l:
        output.add(tuple(item))
    if not l:
        output.add(tuple())
    return output

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default="_", help="Starting game pattern: '_' means repeating copies of q")
    parser.add_argument("--q", default="xxo", help="Repeating pattern")
    parser.add_argument("--prefixes", nargs="+", default=[], help="Set of prefixes")
    parser.add_argument("--suffixes", nargs="+", default=[], help="Set of suffixes")
    parser.add_argument("--json", type=str, metavar="FOLDER", help="Produce JSON output in the given folder")
    parser.add_argument("--conj", default=False, help="Test conjecture that x can win by making leftmost move")

    args = parser.parse_args()

    outcome, nodes = generator.run(args.state, args.q, parse(args.prefixes), parse(args.suffixes), args.json, conj=args.conj)
    print(f"Outcome class: {outcome}")
    print(f"Nodes visited: {nodes}")

if __name__ == "__main__":
    main()