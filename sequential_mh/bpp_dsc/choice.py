from operator import itemgetter
from typing import List, Tuple

from .support import dfs
from .tree import Operations, Tree, is_cc_node, is_rolling_node, solution_efficiency


def choose_tree(trees: List[Tree], aspect_ratio=10) -> Tuple[Tree, float]:
    """Выбор дерева на основе эффективности и количество прокатов"""
    # if trees[0]._type == 0:
    #     print()
    #     print()
    #     print('-' * 50)
    ef_trees = [
        (tree, solution_efficiency(
            tree.root, list(dfs(tree.root)), tree.main_kit,
            max_aspect_ratio=aspect_ratio, nd=True, is_p=True
        )) for tree in trees
    ]
    ef_trees.sort(key=itemgetter(1), reverse=True)

    # if ef_trees[0][0]._type == 0:
    #     print('-' * 50)
    #     for i, (t, count, ef) in enumerate(ef_trees):
    #         print(f'Решение {i} ({t}): {ef}; {count}; {number_annealing(t.root)}')
    #     print('-' * 50)
    #     print()
    #     print()

    # for i, (t, ef) in enumerate(ef_trees):
    #     total_ef = solution_efficiency(
    #         t.root, list(dfs(t.root)), t.main_kit, is_total=True
    #     )
    #     total_norm_ef = solution_efficiency(
    #         t.root, list(dfs(t.root)), t.main_kit, is_total=True, nd=True
    #     )
    #     local_ef = solution_efficiency(
    #         t.root, list(dfs(t.root)), t.main_kit
    #     )
    #     local_norm_ef = solution_efficiency(
    #         t.root, list(dfs(t.root)), t.main_kit, nd=True
    #     )
    #     print(f'{i}: {ef=:.4f}; {total_ef=:.4f}; {total_norm_ef=:.4f}; {local_ef=:.4f}; {local_norm_ef=:.4f}; {number_rolling(t.root)}')

    max_efficiency = ef_trees[0][1]

    ef_trees = list(filter(lambda item: item[1] >= max_efficiency - 0.02, ef_trees))

    # if trees[0]._type == 0:
    #     print()
    #     print('После фильтрации')
    #     print('-' * 50)
    #     for i, (t, ef) in enumerate(ef_trees):
    #         print(f'Решение {i} ({t}): {ef}; {number_rolling(t.root)}')
    #     print('-' * 50)
    #     print()
    #     print()

    # print(f'Количество кандидатов {len(ef_trees)}:')
    # for tree, efficiency in ef_trees:
    #     print(f'Узлов проката: {number_rolling(tree.root)}; эффективность: {efficiency:.6f}')

    best = min(ef_trees, key=lambda item: number_rolling(item[0].root))
    # print(f'Выбор: Узлов проката: {number_rolling(best[0].root)}; эффективность: {best[1]:.6f}')
    return best


def number_rolling(root) -> int:
    """Количество прокатов"""
    number = 0
    for node in dfs(root):
        if is_rolling_node(node) and node.operation in (Operations.h_rolling, Operations.v_rolling):
            parent_bin_node = node.parent_bnode
            if parent_bin_node and round(parent_bin_node.bin.height, 4) != round(node.children.bin.height, 4):
                number += 1
        elif is_cc_node(node):
            for subtree in node.subtree:
                number += number_rolling(subtree.root)
    return number
