import matplotlib.pyplot as plt


def size_dependencies():
    """Область допустимых размеров листа"""
    W_0 = 100
    L_0 = 160
    H_0 = 10
    H_1 = 3

    x = []
    i = 100
    while i < W_0*H_0 / H_1:
        x.append(i)
        i += 0.1

    y_1 = [L_0 * W_0 * H_0 / (H_1 * i) for i in x]
    y_2 = [j - 15 for j in y_1]

    _, axis = plt.subplots()
    axis.plot(x, y_1, color='b', label='Максимальная граница размеров')
    axis.hlines(y_1[0], 0, W_0, color='b')
    axis.hlines(0, 0, x[-1], color='b')
    axis.vlines(x[-1], 0, L_0, color='b')
    axis.vlines(0, 0, y_1[0], color='b')
    axis.plot(x, y_2, color='g', label='Верхняя кромка')
    axis.legend()
    axis.grid()

    plt.show()


def hem_and_end():
    """Поведение кромок/торцов"""
    # изначальные размеры
    W_0, L_0, H_0 = 100, 160, 10
    H_1 = 3
    top_hem = 15  # верхняя кромка/торец
    right_hem = 5  # правая кромка

    x = []
    i = W_0
    while i < W_0*H_0 / H_1:
        x.append(i)
        i += 0.1

    y = []
    i = L_0
    while i < L_0*H_0 / H_1:
        y.append(i)
        i += 0.1

    # исходные границы
    y_1 = [L_0 * W_0 * H_0 / (H_1 * i) for i in x]
    x_1 = [L_0 * W_0 * H_0 / (H_1 * i) for i in y]

    # верхняя и правая кромки
    y_2 = [i - top_hem for i in y_1]
    x_2 = [i - right_hem for i in x_1]

    # варианты расположения точек
    # point = (110, 250)  # точка внутри области
    point = (202, 255)  # точка в области кромки/торца
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
    print(min_x, min_y)

    _, axis = plt.subplots()
    axis.plot(x, y_1, color='b', label='Максимальная граница размеров')
    axis.hlines(y_1[0], 0, W_0, color='b')
    axis.hlines(0, 0, x[-1], color='b')
    axis.vlines(x[-1], 0, L_0, color='b')
    axis.vlines(0, 0, y_1[0], color='b')
    axis.plot(x, y_2, color='g', label='Верхняя кромка')
    axis.plot(x_2, y, color='r', label='Правая кромка')
    # axis.plot(x_1, y, color='g', label='Максимальная граница размеров')

    axis.plot(*point, marker='o')
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
    axis.grid()

    plt.show()


if __name__ == '__main__':
    # size_dependencies()
    hem_and_end()
