import os

from sequential_mh.bpp_dsc.rectangle import Material, Blank, Kit, Bin, BinType
from sequential_mh.bpp_dsc.tree import BinNode, Tree, optimal_configuration, solution_efficiency
from sequential_mh.bpp_dsc.stm import _stmh_idrd
from sequential_mh.bpp_dsc.graph import plot, create_edges


os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin'


def main(use_graphviz=False):
    material = Material('Сплав 1', 2.2, 1.)
    data = [
        (160, 93, 3, 1),
        (160, 93, 3, 1),
        (160, 93, 3, 1),
        (160, 93, 3, 1),
        (200, 100, 1, 1),
        (415, 170, 0.5, 1),
        (77, 180, 3.3, 1),
        (77, 180, 3.3, 1),
        (82, 180, 2.2, 1),
        (82, 180, 2.2, 1),
        (420, 165, 0.5, 1),
        (420, 170, 1., 1),
        (420, 170, 1., 1),
    ]
    restrictions = {
        # 'max_size': ((380, 1200), (400, 1200)),  # <= 3, > 3
        # 'end': 0.02,  # обработка торцов листа, в долях
        'cutting_length': 1200,  # максимальная длина реза
        'hem_until_3': 10,  # кромка > 3 мм
        'hem_after_3': 5,  # кромка <= 3 мм
    }
    kit = []
    for item in data:
        kit.append(Blank(*item, material=material))
    kit = Kit(kit)
    # bin_ = Bin(90, 50, 6, material=material, bin_type=BinType.ingot)
    bin_ = Bin(180, 160, 28, material=material, bin_type=BinType.ingot)
    root = BinNode(bin_, kit=kit)
    tree = Tree(root)
    tree = _stmh_idrd(tree, restrictions=restrictions)
    print(f'{root.estimate_size() = }')

    # graph1, all_nodes1 = plot(tree.root, 'graph1.gv')
    # create_edges(tree.root, graph1, all_nodes1)
    # graph1.view()

    efficiency, res, nodes = optimal_configuration(tree, nd=False)
    res.update_size()

    print(f'Всего деталей: {res.kit.qty()}')
    print(f'По всему объему: {solution_efficiency(res, nodes, is_total=True)}')
    print(f'По используемому объему: {solution_efficiency(res, nodes)}')
    print(f'Взвешанная: {solution_efficiency(res, nodes, nd=True)}')

    if use_graphviz:
        graph1, all_nodes1 = plot(res, 'pdf/graph3.gv')
        create_edges(graph1, all_nodes1)
        graph1.view()


if __name__ == '__main__':
    USE_GRAPHVIZ = False
    main(USE_GRAPHVIZ)
