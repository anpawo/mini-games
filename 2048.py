#!/usr/bin/env python3


import sys
import time
import os
import readchar
import random


KeyBind = {
    readchar.key.LEFT: (-1, 0),
    readchar.key.RIGHT: (1, 0),
    readchar.key.UP: (0, -1),
    readchar.key.DOWN: (0, 1),
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

    def __init__(self, seed: int = int(time.time())) -> None:
        # Random
        self.seed = seed

        random.seed(self.seed)

        # Game
        self.score = 0
        self.board = [[(EMPTY_TILE, HASNT_FUSED) for _ in range(4)] for _ in range(4)]
        self.boardIsFull = False
        self.tilesMoved = False

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

    # display
    def __str__(self) -> str:
        """
        ┌─┬─┐
        ├─┼─┤
        └─┴─┘
        """
        seed = f"Seed: {self.seed}\n"
        score = f"Score: {self.score}\n"
        keybinds = "(⭠ ) Left\n(⭢ ) Right\n( ⭡) Up\n( ⭣) Down\n"
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
                board += "┐"  # type: ignore
            else:
                board += "┤"  # type: ignore
            board += "\n"

            for x in range(4):
                v = self.board[y][x][0]
                board += f"│{' ' if v == EMPTY_TILE else v:^4}"
            board += "│\n"

        # last line
        board += "└" + (("─" * 4) + "┴") * 3 + ("─" * 4) + "┘\n"

        return seed + score + board + keybinds

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
                if self.board[y][x] == 0:
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
    game = Game() if len(sys.argv) == 1 else Game(int(sys.argv[1]))
    while True:
        # Display game state
        clearTerminal()
        print(game)

        # Check loss
        if game.isLost():
            print(f"Game Over. Score: {game.score}.")
            break

        # Get the input of the player
        ch = readchar.readkey()

        if ch == "q" or ch == "\x04":
            break

        # Compute the input
        game.moveTiles(*KeyBind[ch])

        # Spawn next tile
        game.spawnNextTile()


if __name__ == "__main__":
    main()

# TODO:
"""
- use EMPTY_TILE
- add some colors
"""
