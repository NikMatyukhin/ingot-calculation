"""Алгоритм последовательной древовидной метаэвристики.

:Date: 20.02.2021
:Version: 0.1
:Authors:
    - Воронов Владимир Сергеевич
"""

from collections import deque

from .tree import Operations, is_cc_node, is_op_node, is_adj_node, is_ubin_node


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


def stmh_idrd(tree, sorting='width', rf=None):
    pass


def _stmh_idrd(tree, local=False, restrictions=None):
    if local:
        print('-> Локальная оптимизация')
        level = deque(tree.root.leaves())
        for node in tree.root.cc_leaves:
            parent = node.parent_bnode.parent_bnode
            add_detail = get_unpacked_item(parent, node)
            node.kit.update(add_detail)
    else:
        print('-> Построение дерева')
        level = deque([tree.root])

    while level:
        # 1) Фильтрация узлов (пустой набор для бинов и карт; проверка
        #       размеров для бинов и карт (если у карт не хватает места
        #       - удаление группы толщины))
        level = [node for node in level if not is_empty_node(node)]
        if not level:
            break
        # 2) Сортировка по приоритету, толщине и типу (узлы карт должны
        #       идти перед бинами, но приоритет и толщина должны иметь
        #       первостепенное влияние)
        level = deque(sorted(level, key=predicate))
        # 3) получить первую ноду (без удаления)
        # node = level[0]
        # 4) если она типа 'карта раскроя':
        if is_cc_node(level[0]):
            _pack(level[0], level, restrictions)
        else:
            # 5) иначе (нужна вставка шаблона):
            # 5.1) получить первую ноду (с удалением из уровня)
            node = level.popleft()
            _create_insert_template(node, level, tree, local, restrictions)

    return tree


def _pack(node, level, restrictions):
    if restrictions:
        # максимальная длина реза
        max_len = restrictions.get('cutting_length')
        max_size = restrictions.get('max_size')
        if is_ubin_node(node):
            height = node.bin.d_height
        else:
            height = node.bin.height
        if max_size:
            max_size = max_size[height > 3]
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
        # 4.4.2) упаковать (проверка набора на пустоту внутри
        # метода pack)
        node.pack(max_size=max_size, restrictions=restrictions)
        adj_cc_node.pack(max_size=max_size, restrictions=restrictions)

        rolling_node = cur_branch.parent

        rolling_node.delete(adj_branch)
        rolling_node.parent.parent.update_size(max_len=max_len)
        print(node.result.total_efficiency(*node.bin.size[:2]))
        rolling_node.direction = None

        rolling_node.delete(cur_branch)
        rolling_node.add(adj_branch)
        # adj_branch.update_size(max_len=max_len)
        rolling_node.parent.parent.update_size(max_len=max_len)
        print(adj_cc_node.result.total_efficiency(*adj_cc_node.bin.size[:2]))
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
    else:
        max_len = None
    # 5.2) получить неупакованную толщину (уже получена из сортировки)
    height, _ = node.kit.hp_sequence()[0]
    # 5.3) получить место вставки
    #    (а) получить корень шаблона;
    #    (б) получить толщину шаблона;
    #    (в) если она меньше необходимой, повторить шаги (а)-(в)
    #    с использованием корня шаблона как текущего узла
    #    (г) вернуть узел для вставки
    new_parent = node.insertion_point(height)
    if new_parent is not tree.root:
        new_parent.parent.transfer_size(to_right=False)
    if new_parent.size_check(height):
        # 5.4) создание шаблона с корнем в месте вставки
        children = tree.create_template(new_parent, height)
        if local:
            if new_parent.children.operation == Operations.cutting:
                # доупаковка при дочернем разреза
                children[1].parent = None
                children = children[0]
            elif new_parent.children.operation == Operations.rolling:
                children[0].parent = None
                children = children[1]
                if new_parent.children.children.operation == Operations.h_rolling:
                    # доупаковка при дочернем горизонтальном прокате
                    children.delete(children.children[0])
                else:
                    # доупаковка при дочернем вертикальном прокате
                    children.delete(children.children[1])
        # 5.5) вставка шаблона с копированием нижестоящих узлов
        new_parent.insert(children, max_len=max_len)
        # 5.6) обновление наборов у нижестоящих узлов
        # (Может перенести в метод вставки???)
        for item in new_parent.template_leaves(new_parent):
            if is_adj_node(item):
                item.update_kit(height)
        # 5.7) обновление уровня новыми узлами
        for item in new_parent.leaves():
            if item not in level:
                level.append(item)