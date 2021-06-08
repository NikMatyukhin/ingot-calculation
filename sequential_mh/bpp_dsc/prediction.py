"""Алгоритм определения размеров слитка.

:Date: 03.06.2021
:Version: 0.2
:Authors:
    - Воронов Владимир Сергеевич
"""


from ..bpp_dsc.stm import _stmh_idrd
from .tree import is_defective_tree, solution_efficiency
from .support import dfs


def optimal_ingot_size(main_tree, min_size, max_size, restrictions):
    """Определение размеров слитка

    :param main_tree: Основное дерево, содержащее слиток максимальных размеров
    :type main_tree: Tree
    :param min_size: Минимальные размеры слитка, (длина, ширина, высота)
    :type min_size: tuple[number, number, number]
    :param max_size: Максимальные размеры слитка, (длина, ширина, высота)
    :type max_size: tuple[number, number, number]
    :param restrictions: Ограничения
    :type restrictions: dict
    :raises ValueError: если построено некорректное дерево
    :return: Дерево раскроя для полученного слитка
    :rtype: Tree
    """
    min_length, min_width, min_height = min_size

    trees = _stmh_idrd(
        main_tree, restrictions=restrictions, local=False,
        with_filter=False
    )

    for tree in trees:
        # Получение смежного остатка
        if len(tree.root.adj_leaves) > 1:
            raise ValueError('Смежных остатков более 1!')
        adj_node = tree.root.adj_leaves[0]
        # Обнуление размеров смежного остатка
        adj_node.bin.length = 0
        adj_node.bin.width = 0
        # Обновление размеров вышестоящих узлов:
        # Когда дошли до промежуточного узла:
        # обновлять размеры с учетом ограничений на размеры
        adj_node.upward_size_update(min_size=min_size, max_size=max_size)
        root_size = tree.root.bin.size
        if root_size[0] < min_length:
            tree.root.bin.length = min_length
        if root_size[1] < min_width:
            tree.root.bin.width = min_width
        if root_size[2] < min_height:
            tree.root.bin.height = min_height

        # TODO: Проблема в том, что тип разреза не обновляется
        # может случиться так, что резать нужно будет по другому! (в 7 примере)
        tree.root.update_size()

    if restrictions:
        max_leaf_size = restrictions.get('max_size')
    else:
        max_leaf_size = None
    trees = [
        item for item in trees if not is_defective_tree(item, max_leaf_size)
    ]

    best = max(
        trees,
        key=lambda item: solution_efficiency(
            item.root, list(dfs(item.root)), nd=True, is_p=True
        )
    )

    return best
