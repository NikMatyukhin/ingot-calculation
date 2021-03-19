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


if __name__ == '__main__':
    size_dependencies()
