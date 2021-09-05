import pygame
from pygame.constants import KEYDOWN
import Pieces
import random

pygame.font.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700

# Tetris has 20 rows and 10 colunms 
# dimension below is set up to compile that rule
FIELD_WIDTH = 300
FIELD_HEIGHT = 600
BLOCK_SIZE = 30

# set up field location
TOP_LEFT_X = (SCREEN_WIDTH - FIELD_WIDTH) // 2
TOP_LEFT_Y = (SCREEN_HEIGHT - FIELD_HEIGHT)


def create_grid(locked_pos = {}):
    '''
    Create grid and update it
    each cell hold the color value
    '''
    grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]

    for row in range(len(grid)):
        for col in range(len(grid[row])):
            if (col, row) in locked_pos:
                color = locked_pos[(col, row)]
                grid[row][col] = color

    return grid


def draw_grid(window, grid):
    '''
    Draw the playable field/area of the game (grid line)
    '''
    sx = TOP_LEFT_X
    sy = TOP_LEFT_Y

    # draw horizontal grid line
    for i in range(len(grid)):
        pygame.draw.line(window, (128,128,128),
        (sx, sy + i*BLOCK_SIZE), (sx + FIELD_WIDTH, sy + i*BLOCK_SIZE))

    # draw vertical grid line
    for j in range(len(grid[0])):
        pygame.draw.line(window, (128,128,128),
        (sx + j*BLOCK_SIZE, sy), (sx + j*BLOCK_SIZE, sy + FIELD_HEIGHT))

    
def get_shape():
    '''
    randomly generate the next shape
    '''
    return Pieces.Pieces(5, 0, random.choice(Pieces.shapes))


def draw_window(window, grid, score = 0):
    '''
    Displace the window of the game
    and update the window
    '''
    window.fill((0,0,0))
    pygame.font.init()
    font = pygame.font.SysFont('Gill Sans', 60, True)
    label = font.render('Tetris', 1, (255,105,180))
    window.blit(label, ((TOP_LEFT_X + FIELD_WIDTH/2 - label.get_width()//2), 30))

    font = pygame.font.SysFont('Gill Sans', 40, True)
    score = font.render('Score: ' + str(score), 1, (255,105,180))
    window.blit(score, ((TOP_LEFT_X + FIELD_WIDTH + 50), 50))

    # update the grid color i.e. the postion of the piece
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(window, grid[i][j], 
            (TOP_LEFT_X + j*BLOCK_SIZE, TOP_LEFT_Y + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    # Draw a boarder around the playable area
    draw_grid(window, grid)
    hightest_score(window)
    pygame.draw.rect(window, (255,105,180), (TOP_LEFT_X, TOP_LEFT_Y, FIELD_WIDTH, FIELD_HEIGHT), 4)


def convert_shape(piece):
    '''
    convert list shape with '.' & '0' to piece on screen
    '''
    position = []
    form = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(form):
        row = list(line)
        for j, col, in enumerate(row):
            if col == '0':
                position.append((piece.x + j, piece.y + i))

    # offset
    for i, pos in enumerate(position):
        position[i] = (pos[0] - 2, pos[1] - 4)  # try to not offset it

    return position


def valid_space(piece, grid):
    '''
    check if position is avaliable
    '''
    accepted_pos = [[(j,i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]
    
    formed = convert_shape(piece)
    
    for pos in formed:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    
    return True


def check_lost(positions):
    '''
    Check if player lost the game by stacking too high
    '''
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    
    return False


def draw_next_shape(piece, window):
    '''
    displace next shape on the right
    '''
    font = pygame.font.SysFont('Gill Sans', 30, True)
    label = font.render('Next Shape', 1, piece.color)

    sx = TOP_LEFT_X + FIELD_WIDTH + 50
    sy = TOP_LEFT_Y + FIELD_HEIGHT/2 - 100

    form = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(form):
        row = list(line)
        for j, col, in enumerate(row):
            if col == '0':
                pygame.draw.rect(window, piece.color, (sx + j*BLOCK_SIZE, sy + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    
    window.blit(label, (sx, sy - 30))


def clear_row(grid, locked_pos):
    '''
    clear a row if the row is full
    '''
    inc = 0
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (0,0,0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked_pos[(j,i)]
                except:
                    continue
    
    if inc > 0:
        for key in sorted(list(locked_pos), key = lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                new_key = (x, y + inc)
                locked_pos[new_key] = locked_pos.pop(key)

    return inc


def text(window, text, size, color):
    font = pygame.font.SysFont('Gill Sans', size, True)
    words = font.render(text, 1, color)
    window.blit(words, (SCREEN_WIDTH/2 - words.get_width()/2, SCREEN_HEIGHT/2))


def update_score(score):
    with open('score.txt', 'r') as f:
        lines = f.readlines()
        hight_score = lines[0].strip()
    
    with open('score.txt', 'w') as f:
        if score > int(hight_score):
            f.write(str(score))
        else:
            f.write(str(score))


def hightest_score(window):
    with open('score.txt', 'r') as f:
        lines = f.readlines()
        hight_score = lines[0].strip()

    font = pygame.font.SysFont('Gill Sans', 20, True)
    score = font.render('Hightest Score: ' + str(hight_score), 1, (255,105,180))
    window.blit(score, ((TOP_LEFT_X- 50 - score.get_width()), 150))


def main(window):
    '''
    main game function
    '''
    locked_position = {}
    grid = create_grid(locked_position)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    score = 0

    while run:
        grid = create_grid(locked_position)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            
            if event.type == pygame.KEYDOWN:
                # MOVE PIECE TO THE LEFT
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x += 1

                # MOVE PIECE TO THE RIGHT
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x -= 1

                # ROTATE THE PIECE
                if event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not(valid_space(current_piece, grid)) and current_piece.x > 5:
                        current_piece.x -= 1
                    elif not(valid_space(current_piece, grid)) and current_piece.x < 5:
                        current_piece.x += 1

                # ACCELERATE
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.y -= 1
        
        shape_pos = convert_shape(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_position[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_row(grid, locked_position) * 10

        
        draw_window(window, grid, score)
        draw_next_shape(next_piece, window)
        pygame.display.update()

        if check_lost(locked_position):
            run = False
            update_score(score)
            text(window, 'YOU SUCK!',100, (180,0,0))
            pygame.display.update()
            pygame.time.delay(5000)
            pygame.QUIT


def start(window):
    while True:
        window.fill((0,0,0))
        text(window, 'Press any key to start!', 60, (255,255,255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
                main(window)
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
    

window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')
start(window)