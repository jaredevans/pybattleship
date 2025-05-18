import curses
import random
import time

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
    draw_grid(stdscr, comp_display, "Enemy Board (Your Target)", comp_cursor)
    stdscr.addstr("\n")
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

def animate_explosion(stdscr, loser):
    BATTLESHIP = [
        "    |\\_____________________/|    ",
        "   /                         \\   ",
        "  /___________________________\\  ",
        f"  \\   === {loser.upper()} SHIP ===   /  ",
        "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    ]
    EXPLOSION_FRAMES = [
        [
            "         (  )   (   )  )      ",
            "          ) (   )  (  (       ",
            "          ( )  (    ) )       ",
            "        _.-'~~~~~`-._         ",
            "     .-~===========~-._       ",
            "    (  BOOM! BOOM!    )       ",
            "     `-._    ~~~~~~.-'        ",
            "          `---'               "
        ],
        [
            "           ( (      (  )      ",
            "         ) ) )   ) ) )        ",
            "        ( ( (   ( ( (         ",
            "      .-~~~~~~~~~~~~~-.       ",
            "   .-~   FIRE & FLAMES  ~-.   ",
            "  (   BBBBOOOOOOMMMMM!!!   )  ",
            "   `-._    ~~~~~~~   _.-'     ",
            "        `--._____.--'         "
        ],
        [
            "    *  *    *   *     *  *    ",
            "   *  *  ASHES & SMOKE  * *   ",
            "    *   *   *  *   *   *  *   ",
            "    .-~~~~~~~~~~~~~~-.        ",
            "  (      ship hit!     )      ",
            "    `-.____________.-'        "
        ]
    ]
    max_y, max_x = stdscr.getmaxyx()
    ship_y = max_y // 2 - 8
    ship_x = (max_x - len(BATTLESHIP[0])) // 2

    def draw_water():
        for i in range(ship_y + len(BATTLESHIP), max_y):
            stdscr.addstr(i, 0, "~" * (max_x - 1), curses.color_pair(1))

    def draw_ship(offset=0):
        for idx, line in enumerate(BATTLESHIP):
            stdscr.addstr(ship_y + idx + offset, ship_x, line, curses.color_pair(3) | curses.A_BOLD)

    missile_x = ship_x + len(BATTLESHIP[0]) // 2
    missile_y = 2

    # Animate missile falling
    for y in range(missile_y, ship_y + 2):
        stdscr.clear()
        draw_water()
        draw_ship()
        stdscr.addstr(y, missile_x, "|", curses.color_pair(4) | curses.A_BOLD)
        stdscr.refresh()
        time.sleep(0.03)

    # Draw each frame with correct color
    for frame_num, frame in enumerate(EXPLOSION_FRAMES):
        stdscr.clear()
        draw_water()
        draw_ship(offset=1 if frame_num < 2 else 2)
        if frame_num == 0:
            color = curses.color_pair(2) | curses.A_BOLD   # red, fire/explosion
        elif frame_num == 1:
            color = curses.color_pair(7) | curses.A_BOLD   # bright orange (pair 7)
        else:
            color = curses.color_pair(6) | curses.A_DIM    # gray/dim, ashes/smoke
        for idx, line in enumerate(frame):
            y = ship_y + 2 + idx if frame_num < 2 else ship_y + 3 + idx
            stdscr.addstr(y, missile_x - len(line)//2, line, color)
        stdscr.refresh()
        time.sleep(0.45 if frame_num < 2 else 0.85)

def play(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    
    curses.init_pair(1, curses.COLOR_CYAN, -1)      # water
    curses.init_pair(2, curses.COLOR_RED, -1)       # fire/explosion (red)
    curses.init_pair(3, curses.COLOR_WHITE, -1)     # ship (white)
    curses.init_pair(4, curses.COLOR_YELLOW, -1)    # missile (yellow)
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)   # backup/fallback

    if curses.COLORS >= 256:
        curses.init_pair(6, 244, -1)    # gray for ashes/smoke
        curses.init_pair(7, 214, -1)    # orange for explosion
    else:
        curses.init_pair(6, curses.COLOR_BLACK, -1) # fallback: black/dim
        curses.init_pair(7, curses.COLOR_YELLOW, -1) # fallback: yellow for orange

    size = 10
    comp_fleet = place_fleet(size)
    comp_display = [["~"] * size for _ in range(size)]
    player_fleet = place_fleet(size)
    player_display = [row[:] for row in player_fleet]
    comp_cursor = (0, 0)
    computer_moves = set()
    target_stack = []

    while True:
        draw_boards(stdscr, comp_display, comp_cursor, player_display)
        key = stdscr.getch()
        r, c = comp_cursor
        if key in (ord("q"), ord("Q")):
            break
        elif key == ord("e"):
            animate_explosion(stdscr, "test")
            draw_boards(stdscr, comp_display, comp_cursor, player_display)
            continue
        elif key == curses.KEY_UP and r > 0:
            comp_cursor = (r - 1, c)
        elif key == curses.KEY_DOWN and r < size - 1:
            comp_cursor = (r + 1, c)
        elif key == curses.KEY_LEFT and c > 0:
            comp_cursor = (r, c - 1)
        elif key == curses.KEY_RIGHT and c < size - 1:
            comp_cursor = (r, c + 1)
        elif key == ord(" ") and comp_display[r][c] == "~":
            if comp_fleet[r][c] == "S":
                comp_display[r][c] = "X"
            else:
                comp_display[r][c] = "O"
            # Check if player sank all enemy ships.
            if all(comp_display[i][j] == "X" for i in range(size) for j in range(size) if comp_fleet[i][j] == "S"):
                animate_explosion(stdscr, "computer")
                draw_boards(stdscr, comp_display, comp_cursor, player_display,
                            "🎉 You sank the enemy fleet! Press any key to exit.")
                stdscr.getch()
                break

            # --- Computer's Turn ---
            curses.napms(500)
            move = None
            if target_stack:
                move = target_stack.pop(0)
                while move in computer_moves and target_stack:
                    move = target_stack.pop(0)
                if move in computer_moves:
                    move = None
            if move is None:
                possible = [(i, j) for i in range(size) for j in range(size)
                            if (i, j) not in computer_moves and (i + j) % 2 == 0]
                if not possible:
                    possible = [(i, j) for i in range(size) for j in range(size)
                                if (i, j) not in computer_moves]
                move = random.choice(possible)
            computer_moves.add(move)
            pr, pc = move
            if player_fleet[pr][pc] == "S":
                player_display[pr][pc] = "X"
                for nbr in neighbors(pr, pc, size):
                    if nbr not in computer_moves and nbr not in target_stack:
                        target_stack.append(nbr)
            else:
                if player_display[pr][pc] == "~":
                    player_display[pr][pc] = "O"
            # Check if computer sank all player's ships.
            if all(player_display[i][j] == "X" for i in range(size) for j in range(size) if player_fleet[i][j] == "S"):
                animate_explosion(stdscr, "player")
                draw_boards(stdscr, comp_display, comp_cursor, player_display,
                            "😞 The computer sank your fleet! Press any key to exit.")
                stdscr.getch()
                break

if __name__ == "__main__":
    curses.wrapper(play)

