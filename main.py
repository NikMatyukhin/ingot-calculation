# import os

from sequential_mh.tsh.bpp_ts import bpp_ts
from sequential_mh.tsh.visualize import visualize
from sequential_mh.bpp_dsc.rectangle import Material, Blank, Kit

# os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin'


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
    }
    return data


EXAMPLES = [
    example_1,
    example_2
]


def main(example):
    material = Material('Сплав 1', 2.2, 1.)

    if 0 <= example - 1 < len(EXAMPLES):
        data = EXAMPLES[example]()
    else:
        raise ValueError(
            'Некорректный номер примера. '
            f'Доступны примеры с номерами от {1} до {len(EXAMPLES)}'
        )

    kit = []
    for item in data['kit']:
        kit.append(Blank(*item, material=material))
    kit = Kit(kit)
    kit.sort()
    L_0 = data['L0']
    W_0 = data['W0']
    H_0 = data['H0']
    H_1 = data['H1']
    _, main_region, result, _, tailings = bpp_ts(
        L_0, W_0, H_0, H_1, kit[3], hem=(0, 5), allowance=5, is_visualize=True
    )

    print(
        f'Количество размещенных заготовок: {len(result)}/{len(data["kit"])}'
    )
    print(f'Количество остатков: {len(tailings)}')

    visualize(
        main_region, result, tailings,
        xlim=int(W_0*H_0 / H_1) + 1, ylim=int(L_0*H_0 / H_1) + 1
    )


if __name__ == '__main__':
    example = 1
    main(example)
