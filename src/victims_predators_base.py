
# coding: utf-8

# # Командный проект. Задача "Закон джунглей"
# ### Задача из курса ШАД «Яндекс» по Python (с разрешения преподавателя Алексея Зобнина)

# Напишите программу, моделирующую экологическую систему океана, в котором обитают хищники и жертвы. 
# 
# Океан представляется двуxмерным массивом ячеек. В ячейке может находиться либо хищник, либо жертва, либо препятствие. В каждый квант времени ячейки последовательно обрабатываются. Хищник может съесть соседнюю жертву или просто переместиться на соседнюю клетку, добыча также может переместиться на соседнюю клетку. Если в течение некоторого времени хищник ничего не съел, он погибает. Через определенные интервалы времени хищники и жертвы размножаются, если рядом есть свободная ячейка. При этом потомок занимает свободную ячейку. 
# 
# Текущее состояние экрана отображается на экране, желательно в виде графического интерфейса. Моделирование закачивается либо по истечении некоторого числа итераций, либо когда погибнут все хищники или жертвы. 
# 
# Проверьте на этой модели гипотезу о цикличности популяций хищников и жертв. 

# ## Начало решения

from __future__ import print_function
import os
from time import sleep
from random import choice


# Инициализация поля размерами SIZE_X (по горизонтали, т.е. число столбцов) на SIZE_Y (по вертикали, т.е число строк).
# На поле случайным образом бросаются NUM_PRED хищников ('X'), NUM_VIC жертв ('O') и NUM_OBST препятствий ('#').

SIZE_X, SIZE_Y = 10, 4
NUM_PRED, NUM_VIC, NUM_OBST = 2, 4, 4

def initialize_field():
    '''
    Returns a list of SIZE_X lists (each of length SIZE_y)
    with NUM_PRED 'X's (for predators), NUM_VIC 'O's (for victims)
    and NUM_OBST '#'s (for obstacles) in random places. Each remaining element
    contains a '*'.
    '''
    field = [['*'] * SIZE_X for y in range(SIZE_Y)]
    cell_idx = [(x, y) for x in xrange(SIZE_X)
                for y in xrange(SIZE_Y)]
    
    # add predators
    num_pred = NUM_PRED
    while(num_pred):
        col, row = choice(cell_idx)
        if field[row][col] == '*':
            field[row][col] = 'X'
            num_pred -= 1
    
    # add victims
    num_vic = NUM_VIC
    while(num_vic):
        col, row = choice(cell_idx)
        if field[row][col] == '*':
            field[row][col] = 'O'
            num_vic -= 1
    
    # add obstacles
    num_obst = NUM_OBST
    while(num_obst):
        col, row = choice(cell_idx)
        if field[row][col] == '*':
            field[row][col] = '#'
            num_obst -= 1
            
    return field


# Печать поля. Если clear_all влючен, весь предыдущий вывод затрется. В совокупности с функцией sleep из time можно печатать одно и то же поле в разные моменты времени, а не подряд несколько полей.


def clear_output():
    os.system('cls' if os.name=='nt' else 'clear')

def print_field(field, clear_all=True):
    '''
    Prints the field (a list of lists). If the field is big, it sucks :)
    
    :param field - a list of lists
    :param clear_all - whether to clear previous output.
    '''
    if clear_all:
        clear_output()    
    print('/'  * (2 * SIZE_X + 5))
    for col in range(len(field)):
        print('// ', end='')
        for row in range(len(field[0])):
            print(field[col][row], end=' ')
        print('//')
    print('/' * (2 * SIZE_X + 5))


# Обработка одной клетки в один момент времени. Пока реализован только переход в соседнюю клетку. Если это хищник или жертва и рядом (по горизонтали или вертикали) есть свободные клетки, хищник (или жертва) переходит в одну из случайно выбранных свободных клеток.

def process_one_cell(field, (col, row)):
    '''
    If a cell (col, row) is occupied with 'X' or 'O'
    it modifies the field  and returns a new one.
    
    :param field - a list of lists
    :param (col, row) - a tuple with 2 integer coordinates.
                        col should be in [0, SIZE_X - 1],
                        row should be in [0, SIZE_Y - 1]
    :return field, (new_col, new_row) - filed is a modified list of lists,
                   (new_col, new_row) - are the coordinates of a new cell
                   or the old obe if there was no movement
    '''
    if field[col][row] in ['X', 'O']:
        cur_animal = field[col][row]
        possible_moves = []
        for (new_col, new_row) in [(col, min(row + 1, SIZE_X - 1)),
                                  (col, max(row - 1, 0)),
                                  (max(col - 1, 0), row),
                                  (min(col + 1, SIZE_Y - 1), row)]:
            if field[new_col][new_row] == "*":
                possible_moves.append((new_col, new_row))
        if possible_moves:
            new_col, new_row = choice(possible_moves)
            field[new_col][new_row] = cur_animal
            field[col][row] = '*'
            return field, (new_col, new_row)
    return field, (col, row)


# Функция для запуска обработки всех клеток поля. Здесь учитывается, что если на прошлом шаге в некоторую клетку пришел хищник или жертва, то ее уже не надо обрабатывать.

def process_field(field, verbose=False):
    '''
    Applies process_one_cell to each cell with repsect to the fact 
    that a cell should not be processed if it has already been a destination
    of a previous move.
    
    :param field - a list of lists
    :param verbose - whether to print the moves
    
    :return field - a modified list of lists
    '''
    processed_cells = []
    for col in range(SIZE_Y):
        for row in range(SIZE_X):
            if (col, row) not in processed_cells:
                field, (new_col, new_row) = process_one_cell(field, (col, row))
                if (new_col, new_row) != (col, row):
                    if verbose:
                        print("{} steps {}->{}".format(field[new_col][new_row],
                                                       (col, row), (new_col, new_row)))
                    processed_cells.append((new_col, new_row))
    return field
            


# Проверка на игрушечном примере. Посмотрим, как переместились 2 хищника и 3 жертвы за один ход. Чтоб разобраться было проще, напечатаем координаты ходов.


f = initialize_field()
print_field(f)
f = process_field(f, verbose=True)
sleep(1)
print_field(f, clear_all=False)

