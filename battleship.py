import curses, random

FLEET = {2:3, 3:2, 4:2, 5:1}

def place_fleet(size=10):
    grid = [["~"]*size for _ in range(size)]
    for length,count in FLEET.items():
        for _ in range(count):
            placed=False
            while not placed:
                horiz=random.choice([True,False])
                if horiz:
                    r=random.randrange(size)
                    c=random.randrange(size-length+1)
                    coords=[(r,c+i) for i in range(length)]
                else:
                    r=random.randrange(size-length+1)
                    c=random.randrange(size)
                    coords=[(r+i,c) for i in range(length)]
                if all(grid[x][y]=="~" for x,y in coords):
                    for x,y in coords: grid[x][y]="S"
                    placed=True
    return grid

ICONS={"~":("🌊",1),"X":("🔥",2),"O":("○ ",3)}

def draw(stdscr, display, cursor):
    stdscr.clear()
    size = len(display)

    # Header
    stdscr.addstr("   " + "".join(f"{i+1:^5}" for i in range(size)) + "\n")
    stdscr.addstr("  ┌" + "┬".join("────" for _ in range(size)) + "┐\n")

    for r, row in enumerate(display):
        stdscr.addstr(f"{chr(ord('A')+r)} │")
        for c, val in enumerate(row):
            ch, pair = ICONS.get(val, ICONS["~"])
            attr = curses.color_pair(pair)
            if (r, c) == cursor:
                attr |= curses.A_REVERSE
            stdscr.addstr(f" {ch} ", attr)
            stdscr.addstr("│")
        stdscr.addstr("\n")
        if r < size - 1:
            stdscr.addstr("  ├" + "┼".join("────" for _ in range(size)) + "┤\n")

    stdscr.addstr("  └" + "┴".join("────" for _ in range(size)) + "┘\n")
    stdscr.refresh()


def play(stdscr):
    curses.curs_set(0)
    curses.start_color(); curses.use_default_colors()
    curses.init_pair(1,curses.COLOR_CYAN,-1)
    curses.init_pair(2,curses.COLOR_RED,-1)
    curses.init_pair(3,curses.COLOR_YELLOW,-1)

    size=10
    fleet=place_fleet(size)
    display=[["~"]*size for _ in range(size)]
    cursor=(0,0)
    while True:
        draw(stdscr,display,cursor)
        key=stdscr.getch()
        r,c=cursor
        if key in (ord("q"),ord("Q")): break
        elif key==curses.KEY_UP and r>0: cursor=(r-1,c)
        elif key==curses.KEY_DOWN and r<size-1: cursor=(r+1,c)
        elif key==curses.KEY_LEFT and c>0: cursor=(r,c-1)
        elif key==curses.KEY_RIGHT and c<size-1: cursor=(r,c+1)
        elif key==ord(" ") and display[r][c]=="~":
            display[r][c]="X" if fleet[r][c]=="S" else "O"
        if all(display[i][j]=="X" for i in range(size) for j in range(size) if fleet[i][j]=="S"):
            draw(stdscr,display,cursor)
            stdscr.addstr("\n🎉 You sank the entire fleet! Press any key to exit.")
            stdscr.getch(); break

if __name__=="__main__":
    curses.wrapper(play)

