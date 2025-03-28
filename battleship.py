import curses, random

FLEET = {2: 3, 3: 2, 4: 2, 5: 1}

def place_fleet(size=10):
    grid = [["~"] * size for _ in range(size)]
    for length, count in FLEET.items():
        for _ in range(count):
            placed = False
            while not placed:
                horiz = random.choice([True, False])
                if horiz:
                    r = random.randrange(size)
                    c = random.randrange(size - length + 1)
                    coords = [(r, c + i) for i in range(length)]
                else:
                    r = random.randrange(size - length + 1)
                    c = random.randrange(size)
                    coords = [(r + i, c) for i in range(length)]
                if all(grid[x][y] == "~" for x, y in coords):
                    for x, y in coords:
                        grid[x][y] = "S"
                    placed = True
    return grid

# ICONS mapping. On the player's board, the ship ("S") is shown as a ship icon.
ICONS = {
    "~": ("🌊", 1),
    "S": ("🚢", 4),  # player's ship visible on their board
    "X": ("🔥", 2),
    "O": ("○ ", 3)
}

def draw_grid(stdscr, grid, header, cursor=None):
    size = len(grid)
    stdscr.addstr(header + "\n")
    stdscr.addstr("   " + "".join(f"{i+1:^5}" for i in range(size)) + "\n")
    stdscr.addstr("  ┌" + "┬".join("────" for _ in range(size)) + "┐\n")
    for r, row in enumerate(grid):
        stdscr.addstr(f"{chr(ord('A')+r)} │")
        for c, val in enumerate(row):
            ch, pair = ICONS.get(val, ICONS["~"])
            attr = curses.color_pair(pair)
            if cursor is not None and (r, c) == cursor:
                attr |= curses.A_REVERSE
            stdscr.addstr(f" {ch} ", attr)
            stdscr.addstr("│")
        stdscr.addstr("\n")
        if r < size - 1:
            stdscr.addstr("  ├" + "┼".join("────" for _ in range(size)) + "┤\n")
    stdscr.addstr("  └" + "┴".join("────" for _ in range(size)) + "┘\n")

def draw_boards(stdscr, comp_display, comp_cursor, player_display, win_message=None):
    stdscr.clear()
    # Draw enemy board (player's target)
    draw_grid(stdscr, comp_display, "Enemy Board (Your Target)", comp_cursor)
    stdscr.addstr("\n")
    # Modify the header for player's board if there's a win message
    if win_message:
        header = f"Your Board - {win_message}"
    else:
        header = "Your Board"
    draw_grid(stdscr, player_display, header)
    stdscr.refresh()

def neighbors(r, c, size):
    nbrs = []
    if r > 0:
        nbrs.append((r - 1, c))
    if r < size - 1:
        nbrs.append((r + 1, c))
    if c > 0:
        nbrs.append((r, c - 1))
    if c < size - 1:
        nbrs.append((r, c + 1))
    return nbrs

def play(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)    # water
    curses.init_pair(2, curses.COLOR_RED, -1)     # hit
    curses.init_pair(3, curses.COLOR_YELLOW, -1)  # miss
    curses.init_pair(4, curses.COLOR_GREEN, -1)   # player's ship

    size = 10
    # Computer's board (hidden to the player) and player's view of it.
    comp_fleet = place_fleet(size)
    comp_display = [["~"] * size for _ in range(size)]
    
    # Player's board (visible to the player) - ships are shown.
    player_fleet = place_fleet(size)
    player_display = [row[:] for row in player_fleet]

    # Player's targeting cursor on the enemy board.
    comp_cursor = (0, 0)
    
    # For the computer's hunt/target algorithm:
    computer_moves = set()
    target_stack = []

    # Main game loop: player goes first, then computer's turn.
    while True:
        draw_boards(stdscr, comp_display, comp_cursor, player_display)
        key = stdscr.getch()
        r, c = comp_cursor
        # Player controls
        if key in (ord("q"), ord("Q")):
            break
        elif key == curses.KEY_UP and r > 0:
            comp_cursor = (r - 1, c)
        elif key == curses.KEY_DOWN and r < size - 1:
            comp_cursor = (r + 1, c)
        elif key == curses.KEY_LEFT and c > 0:
            comp_cursor = (r, c - 1)
        elif key == curses.KEY_RIGHT and c < size - 1:
            comp_cursor = (r, c + 1)
        # Player fires a shot on the enemy board.
        elif key == ord(" ") and comp_display[r][c] == "~":
            if comp_fleet[r][c] == "S":
                comp_display[r][c] = "X"
            else:
                comp_display[r][c] = "O"
            # Check if player sank all enemy ships.
            if all(comp_display[i][j] == "X" for i in range(size) for j in range(size) if comp_fleet[i][j] == "S"):
                draw_boards(stdscr, comp_display, comp_cursor, player_display,
                            "🎉 You sank the enemy fleet! Press any key to exit.")
                stdscr.getch()
                break

            # --- Computer's Turn ---
            curses.napms(500)  # brief pause before computer's move

            # Determine computer's move.
            move = None
            # Use target cells if available.
            if target_stack:
                move = target_stack.pop(0)
                # Ensure the move hasn't been tried already.
                while move in computer_moves and target_stack:
                    move = target_stack.pop(0)
                if move in computer_moves:
                    move = None
            # If no target, use hunt mode (choose among parity cells).
            if move is None:
                possible = [(i, j) for i in range(size) for j in range(size)
                            if (i, j) not in computer_moves and (i + j) % 2 == 0]
                if not possible:
                    possible = [(i, j) for i in range(size) for j in range(size)
                                if (i, j) not in computer_moves]
                move = random.choice(possible)
            computer_moves.add(move)
            pr, pc = move

            # Evaluate computer's shot on the player's board.
            if player_fleet[pr][pc] == "S":
                player_display[pr][pc] = "X"
                # Add valid neighbors for targeting.
                for nbr in neighbors(pr, pc, size):
                    if nbr not in computer_moves and nbr not in target_stack:
                        target_stack.append(nbr)
            else:
                if player_display[pr][pc] == "~":
                    player_display[pr][pc] = "O"

            # Check if computer sank all player's ships.
            if all(player_display[i][j] == "X" for i in range(size) for j in range(size) if player_fleet[i][j] == "S"):
                draw_boards(stdscr, comp_display, comp_cursor, player_display,
                            "😞 The computer sank your fleet! Press any key to exit.")
                stdscr.getch()
                break

if __name__ == "__main__":
    curses.wrapper(play)
