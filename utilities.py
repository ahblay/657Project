def generate_test_sequence(pattern, q, length):
    prefix, suffix = pattern.split("_")
    result = []
    cmd1 = 'game.grid.Clobber("'
    cmd2 = '")'
    for i in range(length):
        result.append(f"{cmd1}{prefix}{q*i}{suffix}{cmd2}")
    return result

def clear_file(filename):
    open(f'{filename}.cgs', 'w').close()

def write_to_file(cmds, filename):
    with open(f"{filename}.cgs", "a") as f:
        f.write("x := [")
        counter = 1
        for cmd in cmds:
            f.write(cmd)
            if counter != len(cmds):
                f.write(", ")
            counter += 1
        f.write("];" + "\n")
        f.write(f'System.Print({cmds[0]});\n')
        f.write(f'System.Print({cmds[1]});\n')
        f.write('for g in x do\n\t')
        f.write('System.Print(g.CanonicalForm.OutcomeClass);' + '\n' + 'end')
        f.write('\n\n')
