#!/usr/bin/env python3

import pygame
from pygame.locals import *
from typing import Tuple, Any, List
import time
import random
import copy
import logging

logging.basicConfig(format='%(asctime)s  %(name)s %(levelname)-4s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


def get_color(shape: int):
    logger.info(shape)
    if shape == 0:
        return (255, 0, 0)
    elif shape == 1:
        return (0, 255, 0)
    elif shape == 2:
        return (0, 0, 255)
    elif shape == 3:
        return (255, 255, 0)
    elif shape == 4:
        return (255, 0, 255)
    elif shape == 5:
        return (0, 255, 255)
    elif shape == 6:
        return (255, 255, 255)
    else:
        return (0, 0, 0)


def draw_square(screen: Any, color: Tuple[int, int, int], coord: List[int], size: int, width: int = 2):
    pygame.draw.polygon(screen, color, [
        (coord[0], coord[1]),
        (coord[0] + size, coord[1]),
        (coord[0] + size, coord[1] + size),
        (coord[0], coord[1] + size)
    ], width)


def draw_piece(screen: Any, shape: int, rotation: int, coord: List[int], field_coord: Tuple[int, int], size: int):
    color = get_color(shape)
    for y in range(0, 4):
        for x in range(0, 4):
            if(shapes[shape][rotation] & (0x8000 >> (y * 4 + x))):
                draw_square(screen, color, [(coord[0] + x) * size + field_coord[0], (coord[1] + y) * size + field_coord[1]], size)
    # draw_square(screen, (255, 255, 255), [coord[0] * size + field_coord[0], coord[1] * size + field_coord[1]], 4 * size, 3)


def get_piece_matrix(shape: int, rotation: int) -> List[List[int]]:
    result: List[List[int]] = [[7] * 4 for _ in range(0, 4)]
    for y in range(0, 4):
        for x in range(0, 4):
            if(shapes[shape][rotation] & (0x8000 >> (y * 4 + x))):
                result[y][x] = shape
    return result


def piece_field_intersects(coord: List[int], piece_matrix: List[List[int]], field: List[List[int]]):
    for py in range(0, 4):
        for px in range(0, 4):
            box_x = coord[0] + px
            box_y = coord[1] + py
            piece_shape = piece_matrix[py][px]
            # print(f"box({box_x}, {box_y}, {piece_shape})")
            if piece_shape == 7:
                continue
            if box_x > FIELD_WIDTH - 1:
                return True
            elif box_y > FIELD_HEIGHT - 1:
                return True
            elif box_x < 0:
                return True
            elif box_y < 0:
                return True
            field_shape = field[box_y][box_x]
            if field_shape < 7:
                return True
    return False


def add_piece_matrix_to_field(coord: List[int], piece_matrix: List[List[int]], field: List[List[int]]):
    for y in range(0, 4):
        for x in range(0, 4):
            piece_shape = piece_matrix[y][x]
            if piece_shape < 7:
                field[coord[1] + y][coord[0] + x] = piece_matrix[y][x]


def draw_field(screen: Any, field_coord: List[int], field: List[List[int]]):
    for y in range(0, FIELD_HEIGHT):
        for x in range(0, FIELD_WIDTH):
            if field[y][x] == 7:
                continue
            color = get_color(field[y][x])
            coord = [field_coord[0] + x * block_size, field_coord[1] + y * block_size]
            draw_square(screen, color, coord, block_size, 0)


def move_piece_left(coord: List[int], piece_matrix: List[List[int]], field: List[List[int]]) -> bool:
    if paused:
        return False
    if piece_field_intersects([coord[0] - 1, coord[1]], piece_matrix, field):
        return False
    coord[0] -= 1
    return True


def move_piece_right(coord: List[int], piece_matrix: List[List[int]], field: List[List[int]]) -> bool:
    if paused:
        return False
    if piece_field_intersects([coord[0] + 1, coord[1]], piece_matrix, field):
        return False
    coord[0] += 1
    return True


def move_piece_down(coord: List[int], piece_matrix: List[List[int]], field: List[List[int]]) -> bool:
    if paused:
        return True
    if piece_field_intersects([coord[0], coord[1] + 1], piece_matrix, field):
        return False
    coord[1] += 1
    return True


def check_piece_rotation(shape: int, rotation: int, coord: List[int], field: List[List[int]]) -> bool:
    if paused:
        return False
    next_rotation = rotation + 1
    if next_rotation > 3:
        next_rotation = 0
    if piece_field_intersects(coord, get_piece_matrix(shape, next_rotation), field):
        return False
    return True


def clear_field_lines(field: List[List[int]]):
    delete_count = 0
    copy_field = copy.copy(field)
    copy_field.reverse()
    for i, l in enumerate(copy_field):
        if all(e < 7 for e in l):
            del field[FIELD_HEIGHT - i - 1]
            delete_count += 1
    for _ in range(0, delete_count):
        field.insert(0, [7] * FIELD_WIDTH)

    return delete_count


shapes = [
    [0x4E00, 0x4C40, 0x0E40, 0x4640],  # 'T'
    [0x6C00, 0x8C40, 0x6C00, 0x8C40],  # 'S'
    [0xC600, 0x4C80, 0xC600, 0x4C80],  # 'Z'
    [0x0F00, 0x4444, 0x0F00, 0x4444],  # 'I'
    [0xE200, 0xC880, 0x8E00, 0x44C0],  # 'J'
    [0x2E00, 0xC440, 0xE800, 0x88C0],  # 'L'
    [0xCC00, 0xCC00, 0xCC00, 0xCC00]  # 'O'
]

logger.info("test")
pygame.init()
pygame.font.init()

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FIELD_WIDTH = 10
FIELD_HEIGHT = 20
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

DROP_EVENT = pygame.USEREVENT
RIGHT_SCROLL_EVENT = pygame.USEREVENT + 1
LEFT_SCROLL_EVENT = pygame.USEREVENT + 2
RESET_PIECE = pygame.USEREVENT + 3
DOWN_SCROLL_EVENT = pygame.USEREVENT + 4

pygame.time.set_timer(DROP_EVENT, 500)
pygame.time.set_timer(RIGHT_SCROLL_EVENT, 0)
pygame.time.set_timer(LEFT_SCROLL_EVENT, 0)

running = True
block_size = 20


def generate_random_piece() -> Tuple[int, int, List[int], List[List[int]]]:
    new_shape = random.randint(0, 6)
    new_rotation = 0
    new_piece_position = [4, 0]
    new_piece_matrix = get_piece_matrix(new_shape, new_rotation)
    return new_shape, new_rotation, new_piece_position, new_piece_matrix


shape, rotation, piece_position, piece_matrix = generate_random_piece()
field_coord = [int((SCREEN_WIDTH - FIELD_WIDTH * block_size) / 2), block_size]
field: List[List[int]] = [[7] * FIELD_WIDTH for _ in range(0, FIELD_HEIGHT)]
score = 0
score_font = pygame.font.SysFont('Comic Sans MS', 30)
paused = False
state = "GAMING"


def render_gaming_screen():
    global shape
    global rotation
    global piece_position
    global paused
    global score
    global piece_matrix

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if check_piece_rotation(shape, rotation, piece_position, field):
                    rotation += 1
                    if rotation > 3:
                        rotation = 0
                    piece_matrix = get_piece_matrix(shape, rotation)
            elif event.key == pygame.K_LEFT:
                move_piece_left(piece_position, piece_matrix, field)
                pygame.time.set_timer(LEFT_SCROLL_EVENT, 100)
            elif event.key == pygame.K_RIGHT:
                move_piece_right(piece_position, piece_matrix, field)
                pygame.time.set_timer(RIGHT_SCROLL_EVENT, 100)
            elif event.key == pygame.K_DOWN:
                if not move_piece_down(piece_position, piece_matrix, field):
                    add_piece_matrix_to_field(piece_position, piece_matrix, field)
                    score += clear_field_lines(field)
                    shape, rotation, piece_position, piece_matrix = generate_random_piece()
                    continue
                pygame.time.set_timer(DOWN_SCROLL_EVENT, 50)
            elif event.key == pygame.K_p:
                paused = not paused
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                pygame.time.set_timer(LEFT_SCROLL_EVENT, 0)
            elif event.key == pygame.K_RIGHT:
                pygame.time.set_timer(RIGHT_SCROLL_EVENT, 0)
            elif event.key == pygame.K_DOWN:
                pygame.time.set_timer(DOWN_SCROLL_EVENT, 0)

        elif event.type == DOWN_SCROLL_EVENT or event.type == DROP_EVENT:
            if not move_piece_down(piece_position, piece_matrix, field):
                if piece_position[1] == 0:
                    state = "GAMEOVER"
                    continue
                add_piece_matrix_to_field(piece_position, piece_matrix, field)
                score += clear_field_lines(field)
                shape, rotation, piece_position, piece_matrix = generate_random_piece()
        elif event.type == LEFT_SCROLL_EVENT:
            move_piece_left(piece_position, piece_matrix, field)
        elif event.type == RIGHT_SCROLL_EVENT:
            move_piece_right(piece_position, piece_matrix, field)
    screen.fill((0, 0, 0))
    draw_field(screen, field_coord, field)
    pygame.draw.rect(screen, (0, 255, 0), [tuple(field_coord), (FIELD_WIDTH * block_size, FIELD_HEIGHT * block_size)], 2)
    draw_piece(screen, shape, rotation, piece_position, (field_coord[0], field_coord[1]), block_size)
    if paused:
        score_image = score_font.render(f"Skor: {score} (PAUSED)", True, (255, 255, 255))
    else:
        score_image = score_font.render(f"Skor: {score}", True, (255, 255, 255))
    screen.blit(score_image, (int((SCREEN_WIDTH - FIELD_WIDTH) / 16), int(SCREEN_HEIGHT / 2)))


def render_gameover_screen():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_y:
                field = [[7] * FIELD_WIDTH for _ in range(0, FIELD_HEIGHT)]
                state = "GAMING"
            elif event.key == pygame.K_n:
                running = False
    screen.fill((0, 0, 0))
    score_image = score_font.render(f"Game over. Continue? (y/n)", True, (255, 255, 255))
    screen.blit(score_image, (int((SCREEN_WIDTH - FIELD_WIDTH) / 3), int(SCREEN_HEIGHT / 2)))


try:
    while running:
        print(piece_position[1])

        if state == "GAMING":
            render_gaming_screen()
        elif state == "GAMEOVER":
            render_gameover_screen()
        time.sleep(0.01)
        pygame.display.flip()

except KeyboardInterrupt:
    print("BYEBYE")
