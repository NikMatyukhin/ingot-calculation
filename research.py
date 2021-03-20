"""Модуль для демонтрации различных аспектов раскроя

:Date: 19.03.2020
:Version: 0.2
:Authors:
    - Воронов Владимир Сергеевич
"""

import math

import matplotlib.pyplot as plt


def size_dependencies(width, length, height, g_height):
    """Область допустимых размеров листа"""

    max_w = width * height / g_height
    steps = math.ceil(max_w / 0.1)
    x = [item for i in range(steps) if (item := width + i * 0.1) < max_w]
    y_1 = [length * width * height / (g_height * i) for i in x]

    _, axis = plt.subplots()
    axis.plot(x, y_1, color='b', label='Максимальная граница размеров')
    axis.hlines(y_1[0], 0, width, color='b')
    axis.hlines(0, 0, x[-1], color='b')
    axis.vlines(x[-1], 0, length, color='b')
    axis.vlines(0, 0, y_1[0], color='b')
    axis.legend()
    axis.grid()

    return x, y_1, axis


def hem_and_end():
    """Поведение кромок/торцов"""
    # изначальные размеры
    W_0, L_0, H_0 = 100, 160, 10
    H_1 = 3
    top_hem = 15  # верхняя кромка/торец
    right_hem = 5  # правая кромка

    x, y_1, axis = size_dependencies(W_0, L_0, H_0, H_1)

    max_l = L_0 * H_0 / H_1
    steps = math.ceil(max_l / 0.1)
    y = [item for i in range(steps) if (item := L_0 + i * 0.1) < max_l]

    # исходные границы
    x_1 = [L_0 * W_0 * H_0 / (H_1 * i) for i in y]

    # верхняя и правая кромки
    y_2 = [i - top_hem for i in y_1]
    x_2 = [i - right_hem for i in x_1]

    # варианты расположения точек
    point = (110, 250)  # точка внутри области
    # point = (202, 255)  # точка в области кромки/торца
    # point = (500, 500)  # точка вне области

    # исходные оценки
    y_est = L_0 * W_0 * H_0 / (H_1 * point[0]) - point[1]
    x_est = L_0 * W_0 * H_0 / (H_1 * point[1]) - point[0]
    print(f'Оценка длины и ширины: {x_est, y_est}')

    x_est_right_hem = x_est - right_hem
    x_est_top_hem = L_0 * W_0 * H_0 / (H_1 * (point[1] + top_hem)) - point[0]
    y_est_top_hem = y_est - top_hem
    y_est_right_hem = L_0 * W_0 * H_0 / (H_1 * (point[0] + right_hem)) - point[1]
    min_x = min(x_est_right_hem, x_est_top_hem)
    min_y = min(y_est_right_hem, y_est_top_hem)
    print(f'Оценка с учетом кромок: {min_x, min_y}')
    print(f'Оценка кромок: {x_est - min_x, y_est - min_y}')

    axis.plot(x, y_2, color='g', label='Верхняя кромка')
    axis.plot(x_2, y, color='r', label='Правая кромка')

    axis.plot(*point, marker='o', color='r', label='Точка оценки')
    axis.plot(point[0] + x_est_right_hem, point[1], marker='o', color='orange')
    axis.plot(point[0], point[1] + y_est_top_hem, marker='o', color='plum')
    axis.plot(point[0] + x_est_top_hem, point[1], marker='o', color='orange')
    axis.plot(point[0], point[1] + y_est_right_hem, marker='o', color='plum')

    axis.hlines(
        point[1], point[0], point[0] + x_est, color='k', linestyle='--'
    )
    axis.vlines(
        point[0], point[1], point[1] + y_est, color='k', linestyle='--'
    )

    axis.legend()
    plt.show()


def hem_and_end_2():
    # изначальные размеры
    W_0, L_0, H_0 = 100, 160, 10
    H_1 = 3
    top_hem = 15  # верхняя кромка/торец
    right_hem = 5  # правая кромка

    # варианты расположения точек
    point = (110, 250)  # точка внутри области
    # point = (202, 255)  # точка в области кромки/торца
    # point = (500, 500)  # точка вне области

    x, _, axis = size_dependencies(W_0, L_0, H_0, H_1)

    border = [L_0 * W_0 * H_0 / (H_1 * (i + right_hem)) - top_hem for i in x]

    _y_est = L_0 * W_0 * H_0 / (H_1 * (point[0] + right_hem)) - top_hem - point[1]
    _x_est = L_0 * W_0 * H_0 / (H_1 * (point[1] + top_hem)) - right_hem - point[0]
    y_est = L_0 * W_0 * H_0 / (H_1 * point[0]) - point[1]
    x_est = L_0 * W_0 * H_0 / (H_1 * point[1]) - point[0]
    print(f'Оценка двойной кромки: {_x_est, _y_est}')
    print(f'Размер кромок: {x_est - _x_est, y_est - _y_est}')

    axis.plot(x, border, label='Граница кромок/торцов')
    axis.vlines(
        point[0], point[1], point[1] + _y_est, linestyle='--', color='k'
    )
    axis.hlines(
        point[1], point[0], point[0] + _x_est, linestyle='--', color='k'
    )
    axis.plot(*point, marker='o', color='r', label='Точка оценки')
    axis.plot(point[0], point[1] + _y_est, marker='o', color='k')
    axis.plot(point[0] + _x_est, point[1], marker='o', color='k')

    axis.legend()
    plt.show()


if __name__ == '__main__':
    # hem_and_end()
    hem_and_end_2()
