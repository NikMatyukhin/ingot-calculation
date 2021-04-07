"""Пример работы с древовидной метаэвристикой"""

import os
from itertools import chain

from sequential_mh.bpp_dsc.rectangle import Direction, Material, Blank, Kit, Bin, BinType
from sequential_mh.bpp_dsc.tree import (
    BinNode, Tree, optimal_configuration, solution_efficiency
)
from sequential_mh.bpp_dsc.stm import stmh_idrd
from sequential_mh.bpp_dsc.graph import plot, create_edges

from sequential_mh.tsh import rect
from sequential_mh.tsh.est import Estimator
from sequential_mh.tsh.visualize import visualize


os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin'


def example_1():
    return {
        'name': 'Пример 12ц',
        'kit': [
            (77, 180, 3.3, 1), (77, 180, 3.3, 1),
            (160, 93, 3, 1), (160, 93, 3, 1), (160, 93, 3, 1), (160, 93, 3, 1),
            (200, 100, 1, 1), (420, 170, 1., 1), (420, 170, 1., 1),
            (82, 180, 2.2, 1), (82, 180, 2.2, 1),
            (415, 170, 0.5, 1), (420, 165, 0.5, 1),
        ],
        'L0': 180,
        'W0': 160,
        'H0': 28,
        'max_size': ((1200, 380), (1200, 400)),
        'cutting_length': 1200,  # максимальная длина реза
        'cutting_thickness': 4.2,  # толщина реза
        'hem_until_3': 10,  # кромка > 3 мм
        'hem_after_3': 5,  # кромка <= 3 мм
        'allowance': 2,  # припуски на разрез
        'end': 0.02,  # обработка торцов листа, в долях от длины
    }


def example_2():
    return {
        'name': 'Синтетический пример 1',
        'kit': [
            (68, 110, 3, 1), (78, 30, 3, 1), (30, 30, 3, 1), (100, 68, 3, 1),
            (110, 18, 3, 1), (110, 18, 3, 1), (110, 18, 3, 1), (110, 18, 3, 1),
            (110, 20, 3, 1), (99, 98, 1, 1), (89, 98, 1, 1), (48.5, 30, 1, 1),
            (48.5, 30, 1, 1), (48.5, 30, 1, 1), (38.5, 30, 1, 1),
            (99, 118, 1, 1), (89, 118, 1, 1), (20, 190, 1, 1), (178, 38, 1, 1),
            (178, 38, 1, 1), (178, 38, 1, 1), (178, 38, 1, 1), (178, 30, 1, 1)
        ],
        'L0': 200,
        'W0': 150,
        'H0': 6,
        'cutting_thickness': 3,  # толщина реза
        'hem_after_3': 5,  # кромка <= 3 мм
        'allowance': 2,  # припуски на разрез
        'end': 0.02,  # обработка торцов листа, в долях от длины
    }


def example_3():
    return {
        'name': 'Синтетический пример 2',
        'kit': [
            (200, 170, 1.0, 1), (160, 93, 3.0, 1), (415, 170, 0.5, 1),
            (420, 165, 0.5, 1), (420, 170, 1.0, 1), (82, 180, 2.2, 1),
            (77, 180, 3.3, 1)
        ],
        'L0': 300,
        'W0': 200,
        'H0': 30,
        'cutting_thickness': 4.2,  # толщина реза
        'hem_until_3': 4,  # кромка > 3 мм
        'hem_after_3': 2,  # кромка <= 3 мм
        'allowance': 2,  # припуски на разрез
        'end': 0.02,  # обработка торцов листа, в долях от длины
    }


def example_4():
    return {
        'name': 'Синтетический пример 3',
        'kit': [
            # TODO: Алгоритм работает не правиль из-за ограничений
            (160, 93, 3.0, 1), (128, 180, 3.2, 1), (150, 180, 2.0, 1),
            (430, 100, 1.0, 1), (430, 100, 1.0, 1), (850, 120, 0.5, 1),
            (430, 180, 0.5, 1), (160, 100, 0.5, 1), (260, 180, 1.0, 1)
        ],
        'L0': 180,
        'W0': 160,
        'H0': 28,
        'max_size': ((1200, 380), (1200, 400)),
        'cutting_length': 1200,  # максимальная длина реза
        'cutting_thickness': 4.2,  # толщина реза
        'hem_until_3': 4,  # кромка > 3 мм
        'hem_after_3': 2,  # кромка <= 3 мм
        'allowance': 2,  # припуски на разрез
        'end': 0.02,  # обработка торцов листа, в долях от длины
    }


def example_5():
    return {
        'name': 'Реальный пример 1',
        'kit': [
            (50, 180, 3.0, 1),
            (122, 417, 0.5, 1), (122, 417, 0.5, 1),
            (103, 417, 0.5, 1), (103, 417, 0.5, 1),
            (32, 350, 0.7, 1), (32, 350, 0.7, 1), (32, 350, 0.7, 1), (32, 350, 0.7, 1)
        ],
        'L0': 100,
        'W0': 180,
        'H0': 28,
        'max_size': ((1200, 380), (1200, 400)),
        'cutting_length': 1200,  # максимальная длина реза
        'cutting_thickness': 4.2,  # толщина реза
        'hem_until_3': 4,  # кромка > 3 мм
        'hem_after_3': 2,  # кромка <= 3 мм
        'allowance': 2,  # припуски на разрез
        'end': 0.02,  # обработка торцов листа, в долях от длины
    }


def example_6():
    return {
        'name': 'Реальный пример 2',
        'kit': [
            (86, 220, 3.0, 1),
            (86, 220, 3.0, 1), (86, 220, 3.0, 1),
            (86, 220, 3.0, 1), (86, 220, 3.0, 1),
            (86, 220, 3.0, 1), (86, 220, 3.0, 1), (54, 160, 3.0, 1)
        ],
        'L0': 100,
        'W0': 180,
        'H0': 28,
        'max_size': ((1200, 380), (1200, 400)),
        'cutting_length': 1200,  # максимальная длина реза
        'cutting_thickness': 4.2,  # толщина реза
        'hem_until_3': 4,  # кромка > 3 мм
        'hem_after_3': 2,  # кромка <= 3 мм
        'allowance': 2,  # припуски на разрез
        'end': 0.02,  # обработка торцов листа, в долях от длины
    }


def example_7():
    return {
        'name': 'Реальный пример 3',
        'kit': [
            (86, 220, 3.0, 1), (76, 110, 3.0, 1), (76, 110, 3.0, 1),
            (76, 110, 3.0, 1), (76, 110, 3.0, 1), (76, 110, 3.0, 1),
            (76, 110, 3.0, 1), (76, 110, 3.0, 1), (76, 110, 3.0, 1),
            (76, 110, 3.0, 1), (76, 110, 3.0, 1), (76, 110, 3.0, 1),
            (76, 110, 3.0, 1)
        ],
        'L0': 100,
        'W0': 180,
        'H0': 23,
        'max_size': ((1200, 380), (1200, 400)),
        'cutting_length': 1200,  # максимальная длина реза
        'cutting_thickness': 4.2,  # толщина реза
        'hem_until_3': 4,  # кромка > 3 мм
        'hem_after_3': 2,  # кромка <= 3 мм
        'allowance': 2,  # припуски на разрез
        'end': 0.02,  # обработка торцов листа, в долях от длины
    }


def example_8():
    return {
        'name': 'Реальный пример 3',
        'kit': [
            (100, 200, 1.0, 1), (100, 200, 1.0, 1),
            (200, 100, 1.0, 1), (200, 100, 1.0, 1), (200, 100, 1.0, 1),
            (200, 100, 1.0, 1),
            (200, 200, 2.0, 1), (200, 200, 2.0, 1), (200, 200, 2.0, 1),
        ],
        'L0': 180,
        'W0': 160,
        'H0': 28,
        'max_size': ((1200, 380), (1200, 400)),
        'cutting_length': 1200,  # максимальная длина реза
        'cutting_thickness': 4.2,  # толщина реза
        'hem_until_3': 4,  # кромка > 3 мм
        'hem_after_3': 2,  # кромка <= 3 мм
        'allowance': 2,  # припуски на разрез
        'end': 0.02,  # обработка торцов листа, в долях от длины
    }


def example_9():
    return {
        'name': '',
        'kit': [
            (200, 100, 1.0, 1, Direction.P),
            (200, 100, 1.0, 1, Direction.P),
            (100, 200, 1.0, 1, Direction.P),
            (100, 200, 1.0, 1, Direction.P),
            (100, 100, 1.0, 1, Direction.A),
            (100, 100, 1.0, 1, Direction.A),
            # (100, 100, 1.0, 1, Direction.A),
            # (100, 100, 1.0, 1, Direction.A),
        ],
        'L0': 180,
        'W0': 160,
        'H0': 15,
        # 'H0': 28,
        'max_size': ((1200, 380), (1200, 400)),
        'cutting_length': 1200,    # максимальная длина реза
        'cutting_thickness': 4.2,  # толщина реза
        'hem_until_3': 4,          # кромка > 3 мм
        'hem_after_3': 2,          # кромка <= 3 мм
        'allowance': 2,            # припуски на разрез
        'end': 0.02,               # торцы листа, в долях от длины
    }


def example_10():
    return {
        'name': '',
        'kit': [
            (200, 170, 1.0, 1, Direction.A),
            (160, 93, 3.0, 1, Direction.A),
            (415, 170, 0.5, 1, Direction.A),
            (420, 165, 0.5, 1, Direction.A),
            (420, 170, 1.0, 1, Direction.A),
            (82, 180, 2.2, 1, Direction.A),
            (77, 180, 3.3, 1, Direction.A),
        ],
        'L0': 180,
        'W0': 160,
        'H0': 28,
        'max_size': ((1200, 380), (1200, 400)),
        'cutting_length': 1200,    # максимальная длина реза
        'cutting_thickness': 4.2,  # толщина реза
        'hem_until_3': 4,          # кромка > 3 мм
        'hem_after_3': 2,          # кромка <= 3 мм
        'allowance': 2,            # припуски на разрез
        'end': 0.02,               # торцы листа, в долях от длины
    }


EXAMPLES = [
    example_1,
    example_2,
    example_3,
    example_4,
    example_5,
    example_6,
    example_7,
    example_8,
    example_9,
    example_10,
]


def main(example, use_graphviz=False):
    material = Material('Сплав 1', 2.2, 1.)
    if 0 <= example - 1 < len(EXAMPLES):
        data = EXAMPLES[example - 1]()
    else:
        raise ValueError(
            'Некорректный номер примера. '
            f'Доступны примеры с номерами от {1} до {len(EXAMPLES)}'
        )
    restrictions = {
        'max_size': data.get('max_size'),
        'cutting_length': data.get('cutting_length'),
        'cutting_thickness': data.get('cutting_thickness'),
        'hem_until_3': data.get('hem_until_3'),
        'hem_after_3': data.get('hem_after_3'),
        'allowance': data.get('allowance'),
        'end': data.get('end'),
    }
    kit = []
    for item in data['kit']:
        # if item[0] == 300:
        #     direction=Direction.P
        # else:
        #     direction=Direction.A
        if len(item) == 5:
            *item, direction = item
        else:
            direction = Direction.A
        kit.append(Blank(*item, material=material, direction=direction))
    kit = Kit(kit)
    bin_ = Bin(
        data['L0'], data['W0'], data['H0'],
        material=material, bin_type=BinType.ingot
    )
    root = BinNode(bin_, kit=kit)
    tree = Tree(root)
    tree = stmh_idrd(tree, restrictions=restrictions)

    if use_graphviz:
        graph1, all_nodes1 = plot(tree.root, 'pdf/graph2.gv')
        create_edges(graph1, all_nodes1)
        graph1.view()

    _, res, nodes = optimal_configuration(tree, nd=True)
    res.update_size()

    if use_graphviz:
        graph1, all_nodes1 = plot(res, 'pdf/graph3.gv')
        create_edges(graph1, all_nodes1)
        graph1.view()

    for node in res.cc_leaves:
        main_rect = rect.Rectangle.create_by_size(
            (0, 0), node.bin.length, node.bin.width
        )
        main_region = Estimator(main_rect, node.bin.height, node.bin.height)
        rectangles = chain.from_iterable(node.result.blanks.values())
        print(f'Карта толщины: {node.bin.height}; упаковано: {node.result.qty()}/{len(kit[node.bin.height][1])}')
        print(f'Прокат: {node.bin.last_rolldir}')
        print(f'Bin ID: {node._id}')
        if hasattr(node, 'x_hem'):
            print(f'{node.x_hem = }')
        visualize(
            main_region, rectangles, node.result.tailings,
            xlim=node.bin.width + 50, ylim=node.bin.length + 50
        )

    print(f'Всего деталей: {res.kit.qty()}')
    print(f'По всему объему: {solution_efficiency(res, nodes, is_total=True)}')
    print(f'По используемому объему: {solution_efficiency(res, nodes)}')
    print(f'Взвешенная: {solution_efficiency(res, nodes, nd=True)}')


if __name__ == '__main__':
    USE_GRAPHVIZ = True
    NUMBER = 10
    main(NUMBER, USE_GRAPHVIZ)
