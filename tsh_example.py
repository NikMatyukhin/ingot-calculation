"""Модуль с примерами использования пакета sequential_mh.tsh

Пакет sequential_mh.tsh реализует алгоритм раскроя в две стороны.
"""

from sequential_mh.tsh.bpp_ts import bpp_ts
from sequential_mh.tsh.visualize import visualize
from sequential_mh.bpp_dsc.rectangle import Material, Blank, Kit


def example_1():
    """Пример расроя № 1"""
    data = {
        'name': 'Реальный пример 1',
        'kit': [
            (110, 76, 3, 1), (76, 110, 3, 1), (76, 110, 3, 1),
            (110, 76, 3, 1), (110, 76, 3, 1), (110, 76, 3, 1),
            (110, 76, 3, 1), (110, 76, 3, 1), (110, 76, 3, 1),
            (110, 76, 3, 1), (110, 76, 3, 1), (110, 76, 3, 1),
            (220, 86, 3, 1)
        ],
        'L0': 100,
        'W0': 180,
        'H0': 23,
        'H1': 3,
        'hem': (0, 5),
        'allowance': 2,
    }
    return data


def example_2():
    """Реальный пример раскрая № 2

    Большинство фигур одинаковы, только одна отличается.
    Прокат должен приоритетно проходить в одну сторону.
    """
    data = {
        'name': 'Реальный пример 2',
        'kit': [
            (54, 160, 3, 1), (220, 86, 3, 1), (86, 220, 3, 1), (86, 220, 3, 1),
            (220, 86, 3, 1), (220, 86, 3, 1), (220, 86, 3, 1), (220, 86, 3, 1)
        ],
        'L0': 100,
        'W0': 180,
        'H0': 28,
        'H1': 3,
        'hem': (0, 5),
        'allowance': 5,
    }
    return data


def example_3():
    data = {
        'name': 'Синтетический пример 2',
        'kit': [
            (5, 6, 1, 1), (3, 2, 1, 1), (1, 3, 1, 1), (3, 1, 1, 1),
            (1, 8, 1, 1), (1, 2, 1, 1), (2, 1, 1, 1), (1, 1, 1, 1),
            (1, 1, 1, 1)
        ],
        'L0': 7,
        'W0': 8,
        'H0': 2,
        'H1': 1,
        'hem': (0, 1),
        'allowance': 0.5,
    }
    return data


def example_4():
    data = {
        'name': 'Синтетический пример 3',
        'kit': [
            (68, 110, 3, 1), (78, 30, 3, 1), (30, 30, 3, 1), (100, 68, 3, 1),
            (110, 18, 3, 1), (110, 18, 3, 1), (110, 18, 3, 1), (110, 18, 3, 1),
            (110, 20, 3, 1)
        ],
        'L0': 200,
        'W0': 150,
        'H0': 6,
        'H1': 3,
        'hem': (0, 5),
        'allowance': 2,
    }
    return data


def example_5():
    data = {
        'name': 'Синтетический пример 4',
        'kit': [
            (99, 98, 1, 1), (89, 98, 1, 1), (48.5, 30, 1, 1), (48.5, 30, 1, 1),
            (48.5, 30, 1, 1), (38.5, 30, 1, 1), (99, 118, 1, 1),
            (89, 118, 1, 1), (20, 190, 1, 1), (178, 38, 1, 1), (178, 38, 1, 1),
            (178, 38, 1, 1), (178, 38, 1, 1), (178, 30, 1, 1)
        ],
        'L0': 305,
        'W0': 100,
        'H0': 3,
        'H1': 1,
        'hem': (0, 5),
        'allowance': 2,
    }
    return data


EXAMPLES = [
    example_1,
    example_2,
    example_3,
    example_4,
    example_5,
]


def main(example):
    material = Material('Сплав 1', 2.2, 1.)

    if 0 <= example - 1 < len(EXAMPLES):
        data = EXAMPLES[example - 1]()
    else:
        raise ValueError(
            'Некорректный номер примера. '
            f'Доступны примеры с номерами от {1} до {len(EXAMPLES)}'
        )

    kit = []
    for item in data['kit']:
        kit.append(Blank(*item, material=material))
    kit = Kit(kit)
    kit.sort(sorting='width')
    L_0 = data['L0']
    W_0 = data['W0']
    H_0 = data['H0']
    H_1 = data['H1']
    hem = data['hem']
    end = 0.02
    if hem[0] > 0:
        y_hem = (hem[0], hem[0])
    else:
        y_hem = (end*L_0*H_0 / H_1, end*L_0*H_0 / H_1)
        print(f'Нижняя кромка: {y_hem[0]}')
        print(f'Верхняя кромка: {y_hem[1]}')
    if hem[1] > 0:
        x_hem = (hem[1], hem[1])
    else:
        x_hem = (end * W_0*H_0 / H_1, end * W_0*H_0 / H_1)
    allowance = data['allowance']
    _, main_region, min_rect, result, _, tailings = bpp_ts(
        L_0, W_0, H_0, H_1, kit[H_1], x_hem=x_hem, y_hem=y_hem,
        allowance=allowance, is_visualize=False
    )

    print(f'Используемый прямоугольник: {min_rect.length, min_rect.width}')
    print(
        f'Количество размещенных заготовок: {len(result)}/{len(data["kit"])}'
    )
    print(f'Количество остатков: {len(tailings)}')

    volume_ingot = L_0 * W_0 * H_0
    volume_blanks = sum(r.rectangle.volume for r in result)
    volume_tailings = sum(r.square * H_1 for r in tailings)
    print(f'Эффективность: {volume_blanks / volume_ingot}')
    print(f'Объем отходов: {volume_tailings / volume_ingot}')
    print(f'Неиспользуемые части: {(volume_ingot - volume_blanks - volume_tailings) / volume_blanks}')

    visualize(
        main_region, result, tailings,
        xlim=int(W_0*H_0 / H_1) + 1, ylim=int(L_0*H_0 / H_1) + 1
    )


if __name__ == '__main__':
    NUMBER = 1
    main(NUMBER)
