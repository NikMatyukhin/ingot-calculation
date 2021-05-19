"""Алгоритм последовательной древовидной метаэвристики.

:Date: 20.02.2021
:Version: 0.1
:Authors:
    - Воронов Владимир Сергеевич
"""

# import os
from collections import deque
from operator import itemgetter
from sequential_mh.bpp_dsc.rectangle import BinType

from .tree import (
    is_cc_node, is_cutting_node, is_ingot_node, is_op_node, is_adj_node,
    is_ubin_node, is_imt_node, delete_all_branch,
    solution_efficiency, is_defective_tree
)
from .support import dfs

# os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin'
# from sequential_mh.bpp_dsc.graph import plot, create_edges


def is_zero_size(length, width, height):
    return length == 0 or width == 0 or height == 0


def is_empty_node(node):
    if is_cc_node(node):
        if is_ubin_node(node.parent.parent) and hasattr(node.bin, 'd_height'):
            return node.kit.is_empty(node.bin.d_height)
        return node.kit.is_empty(node.bin.height)
    if is_adj_node(node):
        return node.kit.is_empty()
    return True


def is_empty_tree(tree):
    is_empty_flags = []
    for node in tree.root.leaves():
        is_empty_flags.append(is_empty_node(node))
    return all(is_empty_flags)


def predicate(node):
    # Узлы с упаковкой должны стоять в начале!
    _h, _p = node.kit.hp_sequence()[0]
    return _p, -_h, not is_cc_node(node)


def potential_efficiency(node):
    # return node.result.total_efficiency(*node.e_size()[:2])
    return node.result.total_efficiency(*node.bin.size[:2])


def get_unpacked_item(parent, node):
    # TODO: пересмотреть или перенести в метод???
    add_detail = {}
    add_detail[node.bin.height] = {}
    for priority, group in parent.kit[node.bin.height].items():
        for item in group:
            n_blank_in_res = node.result.qty_blank(item)
            n_blank_in_kit = parent.kit.qty_blank(item)
            if n_blank_in_res < n_blank_in_kit:
                for _ in range(n_blank_in_kit - n_blank_in_res):
                    if item.priority not in add_detail[node.bin.height]:
                        add_detail[node.bin.height][priority] = []
                    add_detail[node.bin.height][priority].append(item)
    return add_detail


def stmh_idrd(tree, with_filter=True, restrictions=None):
    is_main = True
    trees = _stmh_idrd(
        tree, restrictions=restrictions, local=not is_main,
        with_filter=with_filter
    )

    if restrictions:
        max_size = restrictions.get('max_size')
    else:
        max_size = None
    print(f'Количество деревьев: {len(trees)}')
    if with_filter:
        trees = [item for item in trees if not is_defective_tree(item, max_size)]
    # efficiency = [
    #     solution_efficiency(item.root, list(dfs(item.root)), nd=True) for item in trees
    # ]
    # bests = [
    #     item for item in trees if solution_efficiency(item.root, list(dfs(item.root))) == max(efficiency)
    # ]
    print(f'Годных деревьев: {len(trees)}')
    best = max(trees, key=lambda item: solution_efficiency(item.root, list(dfs(item.root)), nd=True, is_p=True))
    total_efficiency = solution_efficiency(best.root, list(dfs(best.root)), is_total=True)
    print('Построение дерева завершено')
    print(f'Общая эффективность: {total_efficiency:.4f}')
    print(f'Взвешенная эффективность: {solution_efficiency(best.root, list(dfs(best.root)), nd=True):.4f}')
    print(f'Эффективность с приоритетами: {solution_efficiency(best.root, list(dfs(best.root)), is_p=True):.4f}')
    # print(f'Взвешенная эффективность: {efficiency:.4f}')
    print('-' * 50)
    return best


def _stmh_idrd(tree, local=False, with_filter=True, restrictions=None):
    # if local:
    #     level = deque(tree.root.leaves())
    #     for node in tree.root.cc_leaves:
    #         node.kit.update(node.result.unplaced)
    # else:
    #     level = deque([tree.root])

    level = deque([tree])
    result = []

    if restrictions:
        max_size = restrictions.get('max_size')
    else:
        max_size = None

    while level:
        # 1) Фильтрация узлов (пустой набор для бинов и карт; проверка
        #       размеров для бинов и карт (если у карт не хватает места
        #       - удаление группы толщины))
        # level = [
        #     node for node in level
        #     if not is_empty_node(node) and node in tree.root.leaves()
        # ]
        new_level = deque([])
        for _, tree_ in enumerate(level):
            if with_filter and is_defective_tree(tree_, max_size=max_size):
                continue
            if is_empty_tree(tree_):
                result.append(tree_)
            else:
                new_level.append(tree_)
        # level = deque([t for t in level if not is_empty_tree(t)])
        level = new_level
        if not level:
            break
        # 2) Сортировка по приоритету, толщине и типу (узлы карт должны
        #       идти перед бинами, но приоритет и толщина должны иметь
        #       первостепенное влияние)
        # level = deque(sorted(level, key=predicate))
        # 3) получить первую ноду (без удаления)
        # 4) если она типа 'карта раскроя':

        tree = level.popleft()
        nodes = [node for node in tree.root.leaves() if not is_empty_node(node)]
        nodes = deque(sorted(nodes, key=predicate))
        node = nodes[0]
        if is_cc_node(node):
            _pack(node, level, restrictions)
            if is_empty_tree(tree):
                result.append(tree)
            else:
                level.append(tree)
        else:
            # 5) иначе (нужна вставка шаблона):
            # 5.1) получить первую ноду (с удалением из уровня)
            # node = level.popleft()
            _create_insert_template(node, level, tree, local, restrictions)

    return result


def _pack(node, level, restrictions):
    if restrictions:
        # максимальная длина реза
        max_len = restrictions.get('cutting_length')
        max_size = restrictions.get('max_size')
        if is_ubin_node(node.parent_cont):
            height = node.bin.d_height
        else:
            height = node.bin.height
        if max_size:
            max_size = max_size[height >= 3]
    else:
        max_len = None
        max_size = None
    # 4.1) перенос размеров вправо
    node.transfer_size(to_right=True)
    # 4.2) получение соседней ветки
    adj_branch = node.adjacent_branch()
    # 4.3) если ветка не существует:
    if adj_branch is None or not is_op_node(adj_branch):
        # 4.3.1) упаковать
        node.pack(max_size=max_size, restrictions=restrictions)
        # 4.3.2) обновить размеры
        node.update_size(max_len=max_len)
    else:
        # 4.4) иначе:
        # 4.4.1) получить узел карты из соседне ветки
        adj_cc_node = adj_branch.cc_leaves[0]
        cur_branch = node.current_branch()
        rolling_node = cur_branch.parent
        # 4.4.2) упаковать (проверка набора на пустоту внутри
        # метода pack)
        node.pack(max_size=max_size, restrictions=restrictions)
        adj_cc_node.pack(max_size=max_size, restrictions=restrictions)
        # adj_cc_node.update_size()
        delete_all_branch(
            rolling_node, restrictions.get('max_size'), without_root=True
        )

        if len(rolling_node.list_of_children()) != 2:
            if adj_branch is rolling_node.children:
                adj_cc_node.update_size(max_len=max_len)
            if cur_branch is rolling_node.children:
                node.update_size(max_len=max_len)
        else:
            rolling_node.delete(adj_branch)
            rolling_node.parent.parent.update_size(max_len=max_len)
            rolling_node.direction = None

            rolling_node.delete(cur_branch)
            rolling_node.add(adj_branch)
            rolling_node.parent.parent.update_size(max_len=max_len)
            rolling_node.direction = None
            rolling_node.add(cur_branch)

            # 4.4.3) выбрать ветку с минимальной эффективностью
            # (приоритет отдавать веткам с горизонтальным прокатом)
            branches = [(cur_branch, node), (adj_branch, adj_cc_node)]
            min_branch = min(
                reversed(branches),
                key=lambda item: potential_efficiency(item[1])
            )
            # 4.4.4) выбрать ветку с максимальной эффективностью
            max_branch = max(
                branches,
                key=lambda item: potential_efficiency(item[1])
            )
            # 4.4.5) удалить ветку с минимальной эффективностью из
            # дерева и ее узел из уровня
            if min_branch[1] in level:
                level.remove(min_branch[1])
            min_branch[0].parent.delete(min_branch[0])
            max_branch[1].update_size(max_len=max_len)


def _create_insert_template(node, level, tree, local, restrictions):
    if restrictions:
        max_len = restrictions.get('cutting_length')
        cut_thickness = restrictions.get('cutting_thickness')
    else:
        max_len = None
        cut_thickness = None
    # 5.2) получить неупакованную толщину (уже получена из сортировки)
    height, _ = node.kit.hp_sequence()[0]
    max_heigh = max(node.kit.hp_sequence(), key=itemgetter(0))[0]
    # 5.3) получить место вставки
    #    (а) получить корень шаблона;
    #    (б) получить толщину шаблона;
    #    (в) если она меньше необходимой, повторить шаги (а)-(в)
    #    с использованием корня шаблона как текущего узла
    #    (г) вернуть узел для вставки
    new_parent = node.insertion_point(height)
    if new_parent is not tree.root and not is_imt_node(new_parent):
        new_parent.parent.transfer_size(to_right=False)
    if new_parent.size_check(height):
        # 5.4) создание шаблона с корнем в месте вставки
        if is_ubin_node(new_parent):
            node_height = new_parent.bin.d_height
        else:
            node_height = new_parent.bin.height
        if new_parent is tree.root and is_ingot_node(new_parent) and cut_thickness >= max_heigh and cut_thickness < node_height:
            height = cut_thickness
        else:
            cut_thickness = None
        # children = tree.create_template(
        #     new_parent, height, cut_thickness=cut_thickness
        # )
        res = tree.create_template_branches(new_parent, height, cut_thickness=cut_thickness)
        # if local:
        #     if is_cutting_node(new_parent.children):
        #         # доупаковка при дочернем разреза
        #         children[1].parent = None
        #         children = children[0]
        #     elif is_rolling_node(new_parent.children):
        #         children[0].parent = None
        #         children = children[1]
        #         if new_parent.children.children.operation == Operations.h_rolling:
        #             # доупаковка при дочернем горизонтальном прокате
        #             children.delete(children.children[0])
        #         else:
        #             # доупаковка при дочернем вертикальном прокате
        #             children.delete(children.children[1])
        # 5.5) вставка шаблона с копированием нижестоящих узлов
        for new_tree, new_parent, branch in res:
            if new_parent.list_of_children() and not is_cutting_node(branch[0]):
                continue
            new_parent.insert(branch[0], max_len=max_len)
            # 5.6) обновление наборов у нижестоящих узлов
            # (Может перенести в метод вставки???)
            for item in new_parent.template_leaves(new_parent):
                if is_adj_node(item) and item.bin.bin_type != BinType.INTERMEDIATE:
                    item.update_kit(height)
            # 5.7) обновление уровня новыми узлами
            # for item in new_parent.leaves():
            #     if item not in level:
            level.append(new_tree)
    else:
        node.kit.delete_height(height)
        level.append(tree)
