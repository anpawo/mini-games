#!/usr/bin/env python3


import time
import os
import readchar
import random
import argparse


KeyBind = {
    # Movement
    readchar.key.LEFT: (-1, 0),
    readchar.key.RIGHT: (1, 0),
    readchar.key.UP: (0, -1),
    readchar.key.DOWN: (0, 1),
    # Restart
    "r": None,
    # Quit
    "q": None,
    "\x04": None,  # Ctrl + D
}


HAS_FUSED = True
HASNT_FUSED = False
EMPTY_TILE = 0


class Game:
    """
    Rules:
    - a tile can fuse only once per move.
    - the first tile to fuse is the one on the rightest if u press right (same for every direction)
    """

    def __init__(self, seed: None | float, load: None | str = None, score: int = 0) -> None:
        self.score = score
        self.boardIsFull = False
        self.tilesMoved = False

        # Random
        self.seed = seed or time.time()
        random.seed(self.seed)

        # Load game
        if load:
            self.board = [[(int(tile), HASNT_FUSED) for tile in line.split(" ")] for line in open(load).read().split("\n")]
        # Init Game
        else:
            self.board = [[(EMPTY_TILE, HASNT_FUSED) for _ in range(4)] for _ in range(4)]
            for _ in range(2):
                y = random.randint(0, 3)
                x = random.randint(0, 3)
                while self.board[y][x][0] != 0:
                    y = random.randint(0, 3)
                    x = random.randint(0, 3)
                self.board[y][x] = (2, HASNT_FUSED) if random.randint(0, 9) != 0 else (4, HASNT_FUSED)

        # Display
        # self.boardSize = 4
        # self.tileSize = 5

    def display(self) -> None:
        """
        ┌─┬─┐
        ├─┼─┤
        └─┴─┘
        """
        seed = f"Seed:  {self.seed}\n"
        score = f"Score: {self.score}\n"
        keybinds = "(⭠) Left\n(⭢) Right\n(⭡) Up\n(⭣) Down\n\n(r) Restart\n(q) Quit\n"
        board = ""
        for y in range(4):
            # first
            if y == 0:
                board += "┌"
            else:
                board += "├"

            # middle
            if y == 0:
                c = "┬"
            else:
                c = "┼"
            board += ("─" * 4 + c) * 3
            board += "─" * 4

            # last
            if y == 0:
                board += "┐"
            else:
                board += "┤"
            board += "\n"

            for x in range(4):
                v = self.board[y][x][0]
                board += f"│{' ' if v == EMPTY_TILE else v:^4}"
            board += "│\n"

        # last line
        board += "└" + (("─" * 4) + "┴") * 3 + ("─" * 4) + "┘\n"

        print(seed + score + board + keybinds)

    def nextCollision(self, x: int, y: int, vx: int, vy: int) -> tuple[bool, int, int]:
        if 0 <= x + vx <= 3 and 0 <= y + vy <= 3 and self.board[y + vy][x + vx][0] == 0:
            return self.nextCollision(x + vx, y + vy, vx, vy)
        return not (0 <= x + vx <= 3 and 0 <= y + vy <= 3), x, y

    def moveTiles(self, vx: int, vy: int) -> None:
        self.tilesMoved = False
        right = not vx == -1
        up = not vy == -1
        for y in range(3 if up else 0, -1 if up else 4, -1 if up else 1):
            for x in range(3 if right else 0, -1 if right else 4, -1 if right else 1):
                # Nothing happens if empty
                if self.board[y][x][0] == 0:
                    continue

                # Check collisions
                reachedEndBoard, cx, cy = self.nextCollision(x, y, vx, vy)

                if (
                    # Reached end of the board
                    reachedEndBoard
                    or
                    # Collided with tile that already moved
                    self.board[cy + vy][cx + vx][1] == HAS_FUSED
                    or
                    # Collided with different tile
                    self.board[cy + vy][cx + vx][0] != self.board[y][x][0]
                ):
                    if y != cy or x != cx:
                        self.board[cy][cx] = (self.board[y][x][0], HASNT_FUSED)
                        self.board[y][x] = (0, HASNT_FUSED)
                        self.tilesMoved = True
                # Collided with same tile that hasnt moved (we fuse)
                else:
                    self.board[cy + vy][cx + vx] = (self.board[y][x][0] * 2, HAS_FUSED)
                    self.board[y][x] = (0, HASNT_FUSED)
                    self.score += self.board[cy + vy][cx + vx][0]
                    self.tilesMoved = True

    def spawnNextTile(self) -> None:
        if self.boardIsFull or self.tilesMoved == False:
            return

        y = random.randint(0, 3)
        x = random.randint(0, 3)
        while self.board[y][x][0] != 0:
            y = random.randint(0, 3)
            x = random.randint(0, 3)
        self.board[y][x] = (2, HASNT_FUSED) if random.randint(0, 9) != 0 else (4, HASNT_FUSED)

    def isLost(self):
        self.boardIsFull = True

        for y in range(4):
            for x in range(4):
                # Reset fused counter
                self.board[y][x] = (self.board[y][x][0], HASNT_FUSED)
                if self.board[y][x][0] == EMPTY_TILE:
                    self.boardIsFull = False

        if not self.boardIsFull:
            return False

        # Check neighbors
        for y in range(4):
            for x in range(4):
                if (y != 3 and self.board[y][x][0] == self.board[y + 1][x][0]) or (x != 3 and self.board[y][x][0] == self.board[y][x + 1][0]):
                    return False
        return True


def clearTerminal():
    os.system("clear")


def main():
    # Argument Parsing
    parser = argparse.ArgumentParser(description="2048")

    # Seed for game start
    parser.add_argument("--seed", help="load a seed")

    # Load a game and the current score at the time (sadly, it cannot follow the seed you had at the time)
    parser.add_argument("--load", help="load a game")
    parser.add_argument("--score", help="load a score", default=0, type=float)

    args = parser.parse_args()

    # Main Loop
    game = Game(seed=args.seed, load=args.load, score=args.score)

    while True:
        # Display game state
        clearTerminal()
        game.display()

        # Check loss
        if game.isLost():
            print(f"Game Over. Score: {game.score}.")
            break

        # Get the input of the player
        # ch = None
        while (ch := readchar.readkey()) not in KeyBind:
            continue
        if ch == "q" or ch == "\x04":
            return
        if ch == "r":
            game.__init__(seed=args.seed)
            continue

        # Compute the input
        game.moveTiles(*KeyBind[ch])

        # Spawn next tile
        game.spawnNextTile()


if __name__ == "__main__":
    main()
