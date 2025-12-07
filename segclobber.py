import subprocess
from pathlib import Path

def segclobber(position, player):
    binary = Path(__file__).parent / "bin" / "segclobber"
    cwd = binary.parent

    result = subprocess.run(
        [str(binary), str(position), str(player)],
        capture_output=True,
        text=True,
        check=True,
        timeout=100,
        cwd=cwd
    )

    winning_player = result.stdout[0]
    return winning_player

def get_outcome_class(position):
    position = position.replace("x", "B").replace("o", "W")
    left_can_win = True if segclobber(position, "B") == "B" else False
    right_can_win = True if segclobber(position, "W") == "W" else False

    if left_can_win and right_can_win:
        return "N"
    if left_can_win and not right_can_win:
        return "L"
    if not left_can_win and right_can_win:
        return "R"
    if not left_can_win and not right_can_win:
        return "P"

if __name__ == "__main__":
    g = "xoxoxoxoxoxoxoxx"
    oc = get_outcome_class(g)
    print(oc)