"""Алгоритм последовательной древовидной метаэвристики.

:Date: 20.02.2021
:Version: 0.1
:Authors:
    - Воронов Владимир Сергеевич
"""

from collections import deque
from operator import itemgetter
from sequential_mh.bpp_dsc.rectangle import BinType

from .tree import (
    get_max_size, is_cc_node, is_cutting_node, is_ingot_node, is_op_node, is_adj_node,
    is_ubin_node, is_imt_node, delete_all_branch,
    solution_efficiency, is_defective_tree
)
from .support import dfs


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


# def additional_packaging(tree, restrictions=None):
#     adj_node = tree.root.adj_leaves[0]
#     for node in tree.root.cc_leaves:
#         adj_node.kit.update(node.result.unplaced)
#     tree = _stmh_idrd(tree, local=True, restrictions=restrictions)
#     return tree


def stmh_idrd(tree, in_process_filtering=True, postfiltration=True,
              restrictions=None):
    """Последовательная древовидная метаэвристика

    Алгоритм для поиска решения задачи упаковки слитка. Задача
    заключается в изготовлении элементов прямоугольных размеров
    из слитка, который можно резать и деформировать.

    Метод основан на представлении процесса раскроя в виде дерева.
    Где узлы представляют собой операции, состояния листа и карты
    раскроя.

    :param tree: Начальное дерево, представляющее собой корневой узел
                 с набором размещаемых элемнетов.
    :type tree: Tree
    :param in_process_filtering: Флаг фильтрации на соответствие
                                 ограничениям в процессе построения
                                 деревьев, defaults to True
    :type in_process_filtering: bool, optional
    :param postfiltration: Флаг постфильтрации, определяет необходимость
                           фильтрации на соответствие ограничениям
                           деревьев после построения всех возможных
                           вариентов, defaults to True
    :type postfiltration: bool, optional
    :param restrictions: Словарь ограничений, defaults to None
    :type restrictions: dict, optional
    :return: Дерево раскроя
    :rtype: Tree
    """
    is_main = True
    trees = _stmh_idrd(
        tree, restrictions=restrictions, local=not is_main,
        with_filter=in_process_filtering
    )

    if restrictions:
        max_size = restrictions.get('max_size')
    else:
        max_size = None
    print(f'Количество деревьев: {len(trees)}')
    if postfiltration:
        trees = [
            item for item in trees if not is_defective_tree(item, max_size)
        ]
    print(f'Годных деревьев: {len(trees)}')
    best = max(
        trees,
        key=lambda item: solution_efficiency(
            item.root, list(dfs(item.root)), item.main_kit, nd=True, is_p=True
        )
    )
    total_efficiency = solution_efficiency(
        best.root, list(dfs(best.root)), best.main_kit, is_total=True
    )
    weighted_efficiency = solution_efficiency(
        best.root, list(dfs(best.root)), best.main_kit, nd=True
    )
    prioritized_efficiency = solution_efficiency(
        best.root, list(dfs(best.root)), best.main_kit, is_p=True
    )
    print('Построение дерева завершено')
    print(f'Общая эффективность: {total_efficiency:.4f}')
    print(f'Взвешенная эффективность: {weighted_efficiency:.4f}')
    print(f'Эффективность с приоритетами: {prioritized_efficiency:.4f}')
    # print(f'Взвешенная эффективность: {efficiency:.4f}')
    print('-' * 50)
    return best


def _stmh_idrd(tree, local=False, with_filter=True, restrictions=None,
               with_priority=True):
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
        new_level = deque([])
        for _, tree_ in enumerate(level):
            if with_filter and is_defective_tree(tree_, max_size=max_size):
                continue
            if is_empty_tree(tree_):
                result.append(tree_)
            else:
                new_level.append(tree_)
        level = new_level
        if not level:
            break
        # 2) Сортировка по приоритету, толщине и типу (узлы карт должны
        #       идти перед бинами, но приоритет и толщина должны иметь
        #       первостепенное влияние)
        # 3) получить первую ноду (без удаления)
        # 4) если она типа 'карта раскроя':

        tree = level.popleft()
        nodes = [
            node for node in tree.root.leaves() if not is_empty_node(node)
        ]
        nodes = deque(sorted(nodes, key=predicate))
        node = nodes[0]
        if is_cc_node(node):
            _pack(node, level, restrictions, with_priority=with_priority)
            if is_empty_tree(tree):
                result.append(tree)
            else:
                level.append(tree)
        else:
            # 5) иначе (нужна вставка шаблона):
            # 5.1) получить первую ноду (с удалением из уровня)
            _create_insert_template(node, level, tree, local, restrictions)

    return result


def _pack(node, level, restrictions, with_priority=True):
    if restrictions:
        # максимальная длина реза
        min_size = restrictions.get('min_size')
        max_len = restrictions.get('cutting_length')
        max_size = restrictions.get('max_size')
        if is_ubin_node(node.parent_cont):
            height = node.bin.d_height
        else:
            height = node.bin.height
        max_size = get_max_size(max_size, height)
    else:
        min_size = None
        max_len = None
        max_size = None
    # 4.1) перенос размеров вправо
    node.transfer_size(to_right=True, min_size=min_size)
    # 4.2) получение соседней ветки
    adj_branch = node.adjacent_branch()
    # 4.3) если ветка не существует:
    if adj_branch is None or not is_op_node(adj_branch):
        # 4.3.1) упаковать
        node.pack(
            max_size=max_size, restrictions=restrictions,
            min_size=min_size, with_priority=with_priority
        )
        # 4.3.2) обновить размеры
        node.update_size(max_len=max_len, min_size=min_size)
        if node.result.unplaced:
            # if adj_branch._size_check(node.result.unplaced):
            adj_branch.kit.update(node.result.unplaced)
    else:
        # 4.4) иначе:
        # 4.4.1) получить узел карты из соседне ветки
        adj_cc_node = adj_branch.cc_leaves[0]
        cur_branch = node.current_branch()
        rolling_node = cur_branch.parent
        # 4.4.2) упаковать (проверка набора на пустоту внутри
        # метода pack)
        node.pack(max_size=max_size, min_size=min_size, restrictions=restrictions)
        adj_cc_node.pack(max_size=max_size, min_size=min_size, restrictions=restrictions)
        delete_all_branch(
            rolling_node, restrictions.get('max_size'), without_root=True
        )

        if len(rolling_node.list_of_children()) != 2:
            if adj_branch is rolling_node.children:
                adj_cc_node.update_size(max_len=max_len, min_size=min_size)
            if cur_branch is rolling_node.children:
                node.update_size(max_len=max_len, min_size=min_size)
        else:
            rolling_node.delete(adj_branch)
            rolling_node.parent.parent.update_size(max_len=max_len, min_size=min_size)
            rolling_node.direction = None

            rolling_node.delete(cur_branch)
            rolling_node.add(adj_branch)
            rolling_node.parent.parent.update_size(max_len=max_len, min_size=min_size)
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
            max_branch[1].update_size(max_len=max_len, min_size=min_size)


def _create_insert_template(node, level, tree, local, restrictions, direction=0):
    if restrictions:
        max_len = restrictions.get('cutting_length')
        cut_thickness = restrictions.get('cutting_thickness')
        min_size = restrictions.get('min_size')
    else:
        min_size = None
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
        res = tree.create_template_branches(
            new_parent, height, cut_thickness=cut_thickness,
            direction=direction, min_size=min_size
        )
        if res is None:
            node.kit.delete_height(height)
            level.append(tree)
            return
        # 5.5) вставка шаблона с копированием нижестоящих узлов
        for new_tree, new_parent, branch in res:
            if new_parent.list_of_children() and not is_cutting_node(branch[0]):
                continue
            new_parent.insert(branch[0], max_len=max_len, min_size=min_size)
            # 5.6) обновление наборов у нижестоящих узлов
            # (Может перенести в метод вставки???)
            for item in new_parent.template_leaves(new_parent):
                if is_adj_node(item) and item.bin.bin_type != BinType.INTERMEDIATE:
                    item.update_kit(height)
            # 5.7) обновление уровня новыми узлами
            level.append(new_tree)
    else:
        node.kit.delete_height(height)
        level.append(tree)
