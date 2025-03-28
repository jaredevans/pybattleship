# pybattleship
Console-based curses app of the Battleship game

Single player mode.

Initial Game

![Initial Screen](https://i.imgur.com/i7qzqwD.png)

Completed Game

![Completed Screen](https://i.imgur.com/yshgSI1.png)

Here’s a line‑by‑line walkthrough of how this terminal Battleship game is constructed and how it runs:

1️⃣ Constants & Imports

`import curses, random`

**curses** — a built‑in library for building text‑mode UIs (handles keyboard input, cursor movement, colored text, drawing boxes, etc.).

**random** — used to place ships at random locations.

`FLEET = {2:3, 3:2, 4:2, 5:1}`

A dictionary mapping ship length → number of ships of that length.

* Three 2‑cell ships
* Two 3‑cell ships
* Two 4‑cell ships
* One 5‑cell ship

2️⃣ Placing the Fleet (place_fleet)

```
def place_fleet(size=10):
    grid = [["~"]*size for _ in range(size)]
```

Initializes a **size×size grid** filled with "~" (water).

For each ship length & count:

1. Randomly decide orientation (horizontal or vertical).
1. Randomly pick a starting row/column so the ship fits within bounds.
1. Check that all cells in that segment are still "~".
1. If clear, mark those cells with "S" (ship).

Returns the fully populated 2D list.

3️⃣ Display Icons

`ICONS = {"~":("🌊",1), "X":("🔥",2), "O":("○ ",3)}`

Maps each grid value to:

1. A Unicode symbol
1. A curses color pair index

Symbol	Meaning

* 🌊 ("~")	Untried water
* 🔥 ("X")	Hit (ship cell guessed)
* ○ ("O")	Miss (water guessed)

4️⃣ Drawing the Board (draw)

`def draw(stdscr, display, cursor):`

1. Clears the screen.
1. Prints a numbered header (columns 1–10) and lettered rows (A–J).
1. Draws grid lines using Unicode box‑drawing characters.
1. Iterates through each cell of display:
1. Looks up the icon and color pair.
1. If it matches the current cursor position, applies a reverse-video highlight.
1. Refreshes the screen to show updates.

5️⃣ Main Game Loop (play)

`curses.wrapper(play)`

* wrapper initializes curses, calls play, and ensures cleanup on exit.

Inside play:

1. Initialize curses (hide cursor, start color mode, define three color pairs).
1. Generate the hidden fleet with place_fleet(10).
1. Create a 10×10 “display” grid of "~" for the player’s view.
1. Set the cursor start at (0,0) (top-left).

**User Input Handling**

* Arrow keys move the cursor within bounds.
* Spacebar fires at the current cell if untried:
	* If there’s a ship ("S"), mark "X".
	* Otherwise mark "O".
* Press “q” or “Q” to quit anytime.

**Win Condition**

After each shot, check if every ship cell in the hidden fleet `(fleet[i][j]=="S")` has been hit `(display[i][j]=="X")`.

* If true → display victory message and exit.

6️⃣ Controls Summary

**Key	Action**

* ↑ ↓ ← →	Move cursor
* Space	Fire shot
* Q	Quit
* Any key (after win)	Exit

7️⃣ Overall Flow

1. Place ships randomly (hidden).
1. Draw blank board for the player.
1. Move cursor to target a cell.
1. Fire → hit (🔥) or miss (○).
1. Repeat until all ships are sunk → you win 🎉.
