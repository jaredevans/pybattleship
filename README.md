# pybattleship
Console-based curses app of the Battleship game!

Player vs Computer mode.

Initial Game

![Initial Screen](https://i.imgur.com/KuwN02o.png)

Completed Game

![Completed Screen](https://i.imgur.com/BQuWf15.png)

This game is a simple implementation of Battleship using Python’s built-in curses module for a text-based user interface. Here’s a detailed breakdown of its components and flow:

# 1. Fleet Setup and Grid Creation
* Fleet Definition:

	The global variable FLEET = {2: 3, 3: 2, 4: 2, 5: 1} defines the ship sizes and how many of each ship to place. For example, there are three ships of length 2, two of length 3, and so on.

* place_fleet Function:
	
	This function generates a square grid (default 10×10) filled with water ("~"). For each ship (with a given length and count), it randomly decides whether to place the ship horizontally or vertically.
	
	* It computes a list of coordinates for the ship placement.
	* It checks that all intended cells are water (i.e., not already occupied).
	* Once a valid placement is found, it marks the grid cells with "S" to indicate a ship. This function is used to set up both the computer’s hidden fleet and the player’s visible fleet.

# 2. Display and Visual Elements
* ICONS Mapping:

	The dictionary ICONS maps grid symbols to a tuple containing an icon (using emoji) and a curses color pair index. For example:
	
	* "~" (water) is shown as a wave emoji.
	* "S" (ship) is represented as a ship emoji (only visible on the player’s board).
	* "X" and "O" are used for hits and misses respectively.

* draw_grid Function:
	
	This function takes a curses screen (stdscr), a grid, and a header string to display the grid in a structured table format. Key points:
	
	* Column numbers and row letters are added for easy reference.
	* Each cell is drawn using the emoji icon and colored according to the grid value.
	* If a cell is under the player’s targeting cursor, it is highlighted (using the reverse video attribute).

* draw_boards Function:

	This function clears the screen and draws two grids:
	
	* The enemy board (the target board the player interacts with).
	* The player’s own board, which shows the location of the player’s ships.
	* It optionally displays a win message on the player’s board header when the game ends.

# 3. Game Logic and Main Loop
Initialization in play Function:

* The curses library is configured (hiding the cursor, setting up color pairs for water, hit, miss, and player ships).
	
* Two boards are created:

	* comp_fleet: The computer’s actual ship placements (hidden from the player).
	* comp_display: What the player sees when targeting the enemy (initially all water).
	* player\_fleet and player\_display: The player's own board (with ships visible).

* Player Turn:

	* The player moves a targeting cursor across the enemy board using arrow keys.

* Pressing the spacebar fires a shot at the current cursor position:

	* If there is a ship ("S") in comp_fleet, that cell in comp_display is marked as a hit ("X").
	* Otherwise, it is marked as a miss ("O").

* After each shot, the game checks if all enemy ship cells have been hit (win condition for the player).

* Computer Turn:

	After the player's shot, the computer takes a turn using a simple AI:

* Hunt and Target Strategy:

	* A set computer_moves keeps track of all moves already made.
	* The target_stack holds promising coordinates (neighbors of a hit) to try next.
	* If there are cells in target_stack, the computer uses them first (target mode). If not, it selects from “hunt mode” cells—those satisfying a parity condition (using a checkerboard pattern to maximize efficiency).

* Evaluating the Shot:

	* If the computer’s move hits a player's ship, that cell in player_display is updated to a hit ("X") and its neighbors (if not already tried) are added to target_stack for further targeting.
	* If the move is a miss, the corresponding cell is marked with "O".

* The game checks if all the player’s ship cells have been hit, which would signal the computer’s victory.

* Game End:

	The game loop continues until either the player sinks all enemy ships or the computer sinks all the player’s ships. A message is then displayed indicating the winner, and the game waits for a key press before exiting.

# 4. Curses Wrapper
* The game is wrapped in curses.wrapper(play), which takes care of setting up the curses environment and cleaning up afterward when the game finishes.

# Summary
This Python battleship game leverages the curses library to provide a dynamic, terminal-based user interface. The game includes:

* Random placement of fleets using a grid system.
* A visually enhanced display using emoji icons and color.
* Interactive control via keyboard for the player.
* A simple yet effective AI for the computer’s moves, featuring both random (hunt mode) and targeted (when a hit is made) strategies.
* Clear win conditions and board updates that inform the player about the game state in real time.
