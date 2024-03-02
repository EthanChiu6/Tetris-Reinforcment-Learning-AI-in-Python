import pygame, sys
import random
import time

#reset (already implemented at the bottom in if game.game_over)
#reward (bumpiness?)
#play(action) -> left, right, rotate, lock piece
#frame (game_iteration)

pygame.init()

#creating a class to hold the information of the current block
class block:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = random.choice(tetrisAI.Colors)
        self.rotation = 0

#creating a game class to control the current and next block while checking for certain actions (ex. game over)
class tetrisAI:

    #Initializing constants for the game
    WIDTH, HEIGHT = 300, 660
    GRID_SIZE = 30

    #Defining block colors
    Colors = [
        (255, 0, 0),
        (0, 0, 255),
        (0, 255, 0),
        (255, 255, 0),
        (255, 165, 0),
        (128, 0, 128)
    ]

    #Defining block shapes
    Shapes = [
        [
            ['.....',
            '.....',
            '.....',
            'OOOO.',
            '.....'],
            ['.....',
            '..O..',
            '..O..',
            '..O..',
            '..O..']
        ],
        [
            ['.....',
            '.....',
            '..O..',
            '.OOO.',
            '.....'],
            ['.....',
            '..O..',
            '.OO..',
            '..O..',
            '.....'],
            ['.....',
            '.....',
            '.OOO.',
            '..O..',
            '.....'],
            ['.....',
            '..O..',
            '..OO.',
            '..O..',
            '.....']
        ],
        [
            [
            '.....',
            '.....',
            '..OO.',
            '.OO..',
            '.....'],
            ['.....',
            '.....',
            '.OO..',
            '..OO.',
            '.....'],
            ['.....',
            '.O...',
            '.OO..',
            '..O..',
            '.....'],
            ['.....',
            '..O..',
            '.OO..',
            '.O...',
            '.....']
        ],
        [
            ['.....',
            '..O..',
            '..O.',
            '..OO.',
            '.....'],
            ['.....',
            '...O.',
            '.OOO.',
            '.....',
            '.....'],
            ['.....',
            '.OO..',
            '..O..',
            '..O..',
            '.....'],
            ['.....',
            '.....',
            '.OOO.',
            '.O...',
            '.....']
        ],
    ]
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width // tetrisAI.GRID_SIZE)] for _ in range(height // tetrisAI.GRID_SIZE)]
        self.display = pygame.display.set_mode([width, height])
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()
        self.reset()
    
    def new_piece(self):
        shape = random.choice(tetrisAI.Shapes)
        return block(self.width // tetrisAI.GRID_SIZE // 2, 0, shape)

    def valid_move(self, piece, x, y, rotation):
        min_col = 5
        for i, row in enumerate(piece.shape[(piece.rotation + rotation) % len(piece.shape)]):
            for j, cell in enumerate(row):
                try:
                    if cell == 'O' and (
                        self.grid[piece.y + i + y][piece.x + j + x] != 0
                        or piece.x + j + x < 0
                        or piece.x + j + x >= len(self.grid[0])
                        or piece.y + i + y >= len(self.grid)
                    ):
                        return False
                except IndexError:
                    return False
        if (piece.x + x) < (min_col * -1) or (piece.x + x) >= len(self.grid[0]):
            return False
        return True
        
    def clear_lines(self):
        #This function clears the lines which are full and returns the number of lines cleared
        #Research on how this works
        lines_cleared = 0
        lines = []
        for i, row in enumerate(self.grid):
            if all(cell != 0 for cell in row):
                lines.append(i)
                lines_cleared += 1
        self.clear_animation(lines)
        for line in lines:
            del self.grid[line]
            self.grid.insert(0, [0 for _ in range(tetrisAI.WIDTH // tetrisAI.GRID_SIZE)])
        return(lines_cleared)

    def lock_piece(self, piece):
        #This function locks the piece in place
        for i, row in enumerate(piece.shape[piece.rotation % len(piece.shape)]):
            for j, cell in enumerate(row):
                if cell == 'O':
                    self.grid[piece.y + i][piece.x + j] = piece.color
                    
        lines_cleared = self.clear_lines()
        reward = 1 + (lines_cleared**2 * (tetrisAI.WIDTH //tetrisAI.GRID_SIZE))
        self.score += reward
        self.current_piece = self.new_piece()
        return reward
    
    def update(self):
        #move the block down and lock it if the move isn't valid
        if not self.game_over:
            if self.valid_move(self.current_piece, 0, 1, 0):
                self.current_piece.y += 1
                return 0
            else:
                reward = self.lock_piece(self.current_piece)
                return reward
                
    def draw(self, screen, special):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell != 'O':
                    pygame.draw.rect(screen, cell, (x * tetrisAI.GRID_SIZE, y * tetrisAI.GRID_SIZE, tetrisAI.GRID_SIZE - 1, tetrisAI.GRID_SIZE - 1))

        if self.current_piece and special == 0:
            # determine what rotation the piece is currently in then draw it based on the information
            for i, row in enumerate(self.current_piece.shape[self.current_piece.rotation % len(self.current_piece.shape)]):
                for j, cell in enumerate(row):
                    if cell == 'O':
                        pygame.draw.rect(screen, self.current_piece.color, ((self.current_piece.x + j) * tetrisAI.GRID_SIZE, (self.current_piece.y + i) * tetrisAI.GRID_SIZE, tetrisAI.GRID_SIZE - 1, tetrisAI.GRID_SIZE - 1))
        
        pygame.display.update()
        
    def clear_animation(self, lines):
        run = False
        cur = 0
        count = 0
        if len(lines) > 0:
            run = True
        while run:
            if cur == tetrisAI.WIDTH*6000 + 1000:
                run = False
            elif (cur % (tetrisAI.GRID_SIZE*6000)) == 0:
                for temp in range (0, count):
                    if temp >= count-3:
                        for line in lines:
                            self.grid[line][temp] = 'gray95'
                    else:
                        for line in lines:
                            self.grid[line][temp] = 'Black'
                self.draw(self.display, 1)
                pygame.display.flip()
                count += 1
            cur += 0.5  
        
    def play_step(self, x, rotation, tick):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
               
        if self.valid_move(self.current_piece, x, 0, rotation):
            self.current_piece.x += x
                    
        reward = self.update()
        if not self.valid_move(self.current_piece, 0, 0, 0):
            self.game_over = True
            reward -= 10
            return reward, self.game_over, self.score
        
        self.display.fill('BLACK')
        self.draw(self.display, 0)
        self.clock.tick(tick)
        return reward, self.game_over, self.score
        
    def number_of_holes(self):
        count = 0
        for i in range(0, len(self.grid) - 1):
            for j, cell in enumerate(self.grid[i]):
                if cell != 0 and self.grid[i+1][j] == 0:
                    count += 1
        return count

    def bumpiness(self):
        total_bumpiness = 0
        max_bumpiness = 0
        min_ys = []
        
        for col in range(0, len(self.grid[0])):
            count = 0
            row = len(self.grid) - 1
            run = True
            while run:
                if self.grid[row][col] == 0:
                    min_ys.append(count)
                    run = False
                else:
                    count += 1
                    row -= 1
        
        for i in range(len(min_ys) - 1):
            bumpiness = abs(min_ys[i] - min_ys[i+1])
            max_bumpiness = max(bumpiness, max_bumpiness)
            total_bumpiness += abs(min_ys[i] - min_ys[i+1])
        return total_bumpiness, max_bumpiness

    def get_height(self):
        sum_height = 0
        max_height = 0
        min_height = tetrisAI.HEIGHT // tetrisAI.GRID_SIZE
    
        for col in range(0, len(self.grid[0])):
            height = 0
            for row in range((len(self.grid)-1), 0, -1):
                if self.grid[row][col] != 0:
                    height = len(self.grid) - row
            sum_height += height
            if height > max_height:
                max_height = height
            if height < min_height:
                min_height = height
        return sum_height, max_height, min_height
           
    def get_state(self):
        lines = self.clear_lines()
        holes = self.number_of_holes()
        total_bumpiness, max_bumpiness = self.bumpiness()
        sum_height, max_height, min_height = self.get_height()
        return [lines, holes, total_bumpiness, sum_height]     

    def reset(self):
        self.current_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.grid = [[0 for _ in range(tetrisAI.WIDTH // tetrisAI.GRID_SIZE)] for _ in range(tetrisAI.HEIGHT // tetrisAI.GRID_SIZE)]                                                                            