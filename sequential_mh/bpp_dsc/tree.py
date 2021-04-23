"""Реализация дерева для алоритма STM.

:Date: 20.02.2021
:Version: 0.1
:Authors:
    - Воронов Владимир Сергеевич
"""


from collections import deque
from collections.abc import Iterable
from copy import copy, deepcopy
from enum import Enum
from functools import partial
from itertools import chain, product, count


from .ph import ph_bpp
from .support import deformation, is_subrectangle, is_subrectangle_with_def, dfs
from .exception import (
    DirectionError, KitError, ParentNodeError, SizeError,
    ChildrenNodeError, OperationTypeError
)
from .rectangle import BinType, Bin, Direction, Kit, Number, Result, UnsizedBin
from sequential_mh.tsh.bpp_ts import bpp_ts


Vec3 = tuple[Number, Number, Number]


LENGTH = 0
WIDTH = 1
HEIGHT = 2


class WithID:
    """Добавление инкрементального ID в класс
    :ivar _current_id: Счетчик инкрементального ID
    :vartype _current_id: itertools.count
    :ivar _id: Инкрементальный ID
    :vartype _id: int
    """
    _current_id = count()

    def __init__(self) -> None:
        self._id = next(self.__class__._current_id)

    # работа с ID ------------------------------------------------------
    @classmethod
    def reset_id(cls) -> None:
        """Сброс ID"""
        cls._current_id = count()

    @classmethod
    def set_id(cls, value: int) -> None:
        """Установить начальное значение ID"""
        cls._current_id = count(value)

    @property
    def current_id(self) -> int:
        """Получить текущее значение ID"""
        return self._id


class Operations(Enum):
    """Класс типов операций"""
    rolling = 'Прокат'
    v_rolling = 'Вертикальный прокат'
    h_rolling = 'Горизонтальный прокат'
    cutting = 'Разрез'
    packing = 'Упаковка'


class BaseNode(WithID):
    def __init__(self, children=None, parent=None) -> None:
        super().__init__()
        self.parent = parent
        self._children = children

        self.locked = False

    # работа с потомками (создание, добавление, удаление, вставка) -----
    def create(self, *args, **kwargs):
        pass

    def add(self, node) -> None:
        if self._children is None:
            self._children = node
            node.parent = self
        elif isinstance(self._children, list):
            if node not in self._children:
                self._children.append(node)
                node.parent = self
        else:
            self._children = [self._children, node]
            node.parent = self

    def delete(self, node) -> None:
        if isinstance(self._children, list):
            if node in self._children:
                self._children.remove(node)
                node.parent = None
                if len(self._children) == 0:
                    self._children = None
                elif len(self._children) == 1:
                    self._children = self._children[0]
        else:
            if self._children is node:
                self._children = None
                node.parent = None

    def delete_branch(self):
        cur_branch = self.current_branch()
        if cur_branch:
            rolling_node = cur_branch.parent
            if is_cutting_node(rolling_node):
                cur_branch.delete(cur_branch.children)
                return cur_branch
            else:
                rolling_node.delete(cur_branch)
                return rolling_node

    def insert(self, children) -> None:
        pass

    def set_parent(self, children) -> None:
        if isinstance(children, Iterable):
            for node in children:
                node.parent = self
        else:
            children.parent = self

    # получение узлов (потомков, листов и др.) -------------------------
    def list_of_children(self):
        if self._children is None:
            children = []
        elif isinstance(self._children, list):
            children = self._children
        else:
            children = [self._children]
        return children

    def leaves(self):
        leaves = []
        level = deque([self])
        while level:
            node = level.popleft()
            if node.children is None:
                leaves.append(node)
            else:
                level.extend(node.list_of_children())
        return leaves

    def current_branch(self):
        src = self
        node = self.parent
        while node:
            children = node.list_of_children()
            if len(children) == 1:
                if is_ingot_node(node.parent):
                    return node
                src = node
                node = node.parent
            elif len(children) == 0:
                return node
            else:
                branch_root = [item for item in children if item is src][0]
                if is_ingot_node(node):
                    return branch_root
                neighbour = [item for item in children if item is not src][0]
                if neighbour.children is None:
                    src = node
                    node = node.parent
                else:
                    return branch_root
        return None

    def adjacent_branch(self):
        src = node = self
        while node:
            children = node.list_of_children()
            if len(children) != 2:
                src = node
                node = node.parent
            else:
                return [item for item in children if item is not src][0]
        return None

    # свойства ---------------------------------------------------------
    @property
    def root(self):
        if self.parent is None:
            return self
        else:
            return self.parent.root

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, value) -> None:
        for node in self.list_of_children():
            node.parent = None
        self._children = None
        if isinstance(value, Iterable):
            for node in value:
                self.add(node)
        else:
            self.add(value)

    # маические методы -------------------------------------------------
    def __copy__(self):
        return self.__class__()

    def __repr__(self):
        return f'{self.__class__.__name__}({self.children}, {self.parent})'


class Node(BaseNode):
    # работа с размерами (оценка, обновление) --------------------------
    def estimate_size(self, *, start=None):
        start = start or self
        if not self.children:
            return None
        if isinstance(self.children, list):
            estimates = []
            for node in self.children:
                estimates.append(node.estimate_size(start=start))
            return estimates
        return self.children.estimate_size(start=start)

    def update_size(self, *, start=None, max_len=None):
        start = start or self
        for node in self.list_of_children():
            node.update_size(start=start, max_len=max_len)

    # дополнительно (для удобства) -------------------------------------
    def update_kit(self, height):
        for node in self.list_of_children():
            node.update_kit(height=height)

    def get_troot(self, *, start=None):
        if self.parent:
            if not start or not self.is_troot():
                return self.parent.get_troot(start=self)
        return self

    @staticmethod
    def template_leaves(root):
        leaves = []
        level = deque([root])
        while level:
            node = level.popleft()
            if node is root and node.children is None:
                return [root]
            if node is not root and (node.children is None or is_adj_node(node)
                                     or is_cc_node(node)):
                leaves.append(node)
            else:
                level.extend(node.list_of_children())
        return leaves

    # предикаты --------------------------------------------------------
    def is_troot(self):
        return False

    # свойства ---------------------------------------------------------
    @property
    def cc_leaves(self):
        return [node for node in self.leaves() if is_cc_node(node)]

    @property
    def adj_leaves(self):
        return [node for node in self.leaves() if is_adj_node(node)]

    @property
    def parent_bnode(self):
        if is_bin_node(self.parent) or self.parent is None:  # or is_ubin_node(self.parent) 
            return self.parent
        return self.parent.parent_bnode

    @property
    def parent_cont(self):
        is_none = self.parent is None
        if is_none or is_bin_node(self.parent) or is_ubin_node(self.parent):
            return self.parent
        return self.parent.parent_cont

    @property
    def parent_ubnode(self):
        if is_ubin_node(self.parent) or self.parent is None:
            return self.parent
        return self.parent.parent_ubnode

    @property
    def last_rolldir(self):
        if self.parent:
            return self.parent.last_rolldir
        return None

    # маические методы -------------------------------------------------
    def __copy__(self):
        return self.__class__()

    def __repr__(self):
        return f'{self.__class__.__name__}({self.children}, {self.parent})'


class BinNode(Node):
    def __init__(self, bin: Bin, kit: Kit,
                 children=None, parent=None) -> None:
        super().__init__(children=children, parent=parent)
        self.bin = bin
        self.kit = kit

    def create(self, *args, **kwargs):
        bin_spawn_func = {
            BinType.ingot.name: self._create_nodes_ingot,
            BinType.leaf.name: self._create_nodes_leaf,
            BinType.adjacent.name: self._create_nodes_ingot,
            BinType.INTERMEDIATE.name: self._create_nodes_ingot,
            BinType.semifinished.name: self._create_nodes_semifinished,
            BinType.waste.name: lambda *args, **kwargs: None,
            BinType.residue.name: lambda *args, **kwargs: None,
        }
        if self.bin.bin_type:
            spawn_func = bin_spawn_func[self.bin.bin_type.name]
            node = spawn_func(**kwargs)

            return node

    def _create_nodes_ingot(self, **kwargs):
        """Создание потомков для слитка"""

        cut_thickness = kwargs.get('cut_thickness')

        if self.bin.bin_type not in (BinType.ingot, BinType.adjacent, BinType.INTERMEDIATE):
            msg = ('Nodes such as ingot or contiguous can create knots '
                   'for rolling and cutting.')
            raise ParentNodeError(msg)

        if is_ubin_node(self):
            height = self.bin.d_height
        else:
            height = self.bin.height
        # if not cut_thickness or (cut_thickness and height <= cut_thickness):
        if not cut_thickness or height == cut_thickness:
            left = OperationNode(Operations.cutting)
            right = OperationNode(Operations.rolling)
            return left, right
        if cut_thickness == max(self.kit.blanks.keys()):
            return OperationNode(Operations.rolling)
        return OperationNode(Operations.rolling)

    def _create_nodes_leaf(self, **kwargs):
        """Создание потомков для листа"""
        if not is_op_node(self.parent):
            msg = 'A leaf node can only be created by an operation node.'
            raise ParentNodeError(msg)
        if isinstance(self.bin, UnsizedBin) and len(self.bin.last_deformations()) == 1:
            if self.bin.deformations[-1][1] == Direction.V:
                return OperationNode(Operations.h_rolling)
            return OperationNode(Operations.v_rolling)
        if self.parent.operation in (Operations.v_rolling, Operations.h_rolling):
            # создание разрез
            return OperationNode(Operations.cutting)
        # создание проката
        return OperationNode(Operations.rolling)

    def _create_nodes_semifinished(self, **kwargs):
        """Создание потомков для полуфабриката"""
        if self.bin.bin_type != BinType.semifinished:
            msg = ('Only nodes of the semi-finished type '
                   'can create packing nodes.')
            raise ParentNodeError(msg)
        return OperationNode(Operations.packing)

    def insert(self, children, max_len=None):
        temp_children = self.children
        self.children = children
        if temp_children:
            max_height_node = max(
                self.adj_leaves, key=lambda item: item.bin.height
            )
            max_height_node.children = temp_children
            # пустые шаблоны не будут вставляться
            max_height_node.parent.update_size(max_len=max_len)

    def get_template_height(self, root=None):
        root = root or self.get_troot()
        t_leaves = root.template_leaves(root)
        if t_leaves:
            return min(node.bin.height for node in t_leaves)
        msg = f'Узел {root} не имеет потомков типа "Смежный остаток"'
        raise ChildrenNodeError(msg)

    def insertion_point(self, height):
        src = self
        root = self.get_troot()
        while self.get_template_height(root) < height:
            src = root
            root = root.get_troot()
            if is_bin_node(src) and src.bin.bin_type == BinType.ingot:
                break
        return src

    def get_bin_neighbors(self, root):
        neighbors = []
        nodes = [root]
        while nodes:
            node = nodes.pop()
            if (is_bin_node(node) or is_ubin_node(node)) and node is not root:
                if node is not self:
                    neighbors.append(node)
            else:
                nodes.extend(node.list_of_children())
        return neighbors

    def nearest_descendant_bins(self):
        return self.get_bin_neighbors(self)

    # работа с размерами (оценка, обновление) --------------------------
    def estimate_size(self, *, start=None):
        if self._children is None:
            return 0., 0., self.bin.height
        estimate = super().estimate_size(start=start)
        if self.bin.bin_type in (BinType.ingot, BinType.adjacent, BinType.INTERMEDIATE):
            if len(self.list_of_children()) == 2:
                length = max(item[LENGTH] for item in estimate)
                width = max(item[WIDTH] for item in estimate)
                if is_ubin_node(self):
                    height = self.bin.d_height
                else:
                    height = self.bin.height
                return (length, width, height)
        return estimate

    def available_size(self, *, start=None):
        start = start or self
        if self.bin.bin_type in (BinType.ingot, BinType.adjacent, BinType.INTERMEDIATE):
            if self.bin.bin_type in (BinType.ingot, BinType.INTERMEDIATE):
                estimate = self.estimate_size()
                s_1 = self.bin.width * (self.bin.length - estimate[LENGTH])
                s_2 = self.bin.length * (self.bin.width - estimate[WIDTH])
                if s_1 >= s_2:
                    return (self.bin.length - estimate[LENGTH]), self.bin.width, self.bin.height
                return self.bin.length, (self.bin.width - estimate[WIDTH]), self.bin.height
            _, right = self.parent.children
            right_estimate = right.estimate_size()
            if right_estimate[LENGTH] == 0 or right_estimate[WIDTH] == 0:
                return self.parent_bnode.bin.size
            estimate = self.parent.estimate_size()
            if self.parent.direction == Direction.H:
                size = (
                    self.parent_bnode.bin.length - estimate[LENGTH],
                    self.parent_bnode.bin.width,
                    self.bin.height,
                )
            else:
                size = (
                    self.parent_bnode.bin.length,
                    self.parent_bnode.bin.width - estimate[WIDTH],
                    self.bin.height,
                )
            return size

    def size_check(self, height=None, double_sided=True):
        blanks = self.kit.unplaced(self.bin, height)
        dst = self.available_size()
        number = 0
        for item in blanks:
            if item.height == self.bin.height:
                if item.is_rotatable:
                    number += is_subrectangle(item.size, dst, with_rotate=True)
                else:
                    if self.last_rolldir:
                        if self.last_rolldir != item.direction:
                            item.rotate()
                        number += is_subrectangle(
                            item.size, dst, with_rotate=False
                        )
                    msg = f'Узел {self} не имеет направления проката'
                    raise DirectionError(msg)
            else:
                if double_sided:
                    if item.volume <= dst[LENGTH] * dst[WIDTH] * dst[HEIGHT]:
                        number += 1
                else:
                    for i in (Direction.H, Direction.V):
                        if item.direction and item.direction != i:
                            item.rotate()
                        number += is_subrectangle_with_def(
                            item.size, dst, i.value, item.is_rotatable,
                            self.bin.material.extension
                        )
        return number != 0

    def in_right_branch(self):
        node = self
        parent = node.parent
        if node.is_troot():
            return False
        while parent.parent is not None and not parent.is_troot():
            node = parent
            parent = node.parent
        if len(parent.list_of_children()) == 2:
            return node is parent.list_of_children()[1]
        return False

    def _fix_semifinished(self, width, length, max_size=None, **kwargs):
        # print('Фиксация бина полуфабриката')
        p_cont = self.parent_cont
        rolldir = self.bin.last_rolldir
        if is_cutting_node(self.parent):
            estimate = self.parent.children[0].estimate_size()
        else:
            estimate = (0, 0)
        is_locked = False
        if rolldir == Direction.H:
            length = max(length, p_cont.bin.length, estimate[LENGTH])
            is_locked = to_delete(length, width, max_size)
        else:
            width = max(width, p_cont.bin.width, estimate[WIDTH])
            is_locked = to_delete(width, length, max_size)

        self.locked = is_locked
        # if not is_cutting_node(self.parent) and is_locked:
        #     node = self.delete_branch()
        #     return
        bin_ = Bin(
            length, width, self.bin.d_height,
            rolldir, self.bin.material, self.bin.bin_type
        )
        self.bin = bin_
        parent = self.get_parent_ubin()
        parent.fix_sizes(width, length, max_size=max_size, **kwargs)

    def _fix_intermediate(self, width, length, max_size=None, **kwargs):
        # фиксирование промежуточного узла
        p_cont = self.parent_cont
        troot = self.get_troot()
        last_rolldir = self.bin.last_rolldir
        if last_rolldir == Direction.H:
            current_height = (p_cont.bin.d_height - self.bin.d_height) / 2 + self.bin.d_height
            if max_size:
                new_length = max_size[WIDTH]
                if length >= new_length:
                    current_height = length * self.bin.d_height / new_length
                    if current_height > p_cont.bin.d_height:
                        current_height = p_cont.bin.d_height
            # else:
            #     current_height = (p_cont.bin.d_height - self.bin.d_height) / 2 + self.bin.d_height
            length = length * self.bin.d_height / current_height
        else:
            current_height = (p_cont.bin.d_height - self.bin.d_height) / 2 + self.bin.d_height
            if max_size:
                new_width = max_size[WIDTH]
                if width >= new_width:
                    current_height = width * self.bin.d_height / new_width
                    if current_height > p_cont.bin.d_height:
                        current_height = p_cont.bin.d_height
            # else:
            #     current_height = (p_cont.bin.d_height - self.bin.d_height) / 2 + self.bin.d_height
            width = width * self.bin.d_height / current_height
        bin_ = Bin(
            length, width, current_height,
            last_rolldir, self.bin.material, self.bin.bin_type
        )
        self.bin = bin_
        neighbour = self.get_bin_neighbors(troot)
        neighbour = [is_bin_node(node) for node in neighbour]
        if all(neighbour):
            rolling_node = self.parent.parent
            if len(rolling_node.list_of_children()) == 2:
                # выбираем одну из веток проката сразу!!!
                left, right = rolling_node.children
                max_size_ = [(), max_size] if self.bin.d_height > 3 else [max_size, ()]
                delete_left = to_delete_branch(left, max_size_, without_root=False)
                delete_right = to_delete_branch(right, max_size_, without_root=False)
                if delete_left:
                    delete_all_branch(left, max_size_, without_root=False)
                elif delete_right:
                    delete_all_branch(right, max_size_, without_root=False)
                if len(rolling_node.list_of_children()) == 2:
                    left_cc = left.cc_leaves[0]
                    right_cc = right.cc_leaves[0]
                    left_ef = left_cc.result.total_efficiency(*left_cc.parent_bnode.bin.size[:2])
                    right_ef = right_cc.result.total_efficiency(*right_cc.parent_bnode.bin.size[:2])
                    left_ef *= left_cc.result.qty() / self.kit.qty()
                    right_ef *= right_cc.result.qty() / self.kit.qty()
                    length, width, _ = right.estimate_size()
                    # right_dist = self.bin.estimator(width, length, last_deformations)
                    if right_ef >= left_ef:
                        rolling_node.delete(left)
                    else:
                        rolling_node.delete(right)
            troot.fix_sizes(width, length, max_size=max_size, **kwargs)

    def _fix_node_one_def(self, width, length, max_size=None, **kwargs):
        # TODO: провести рефакторинг метода fix_sizes
        pass

    def _fix_node_two_def(self, width, length, max_size=None, **kwargs):
        # TODO: провести рефакторинг метода fix_sizes
        pass

    def _fix_node_withot_def(self, width, length, **kwargs):
        # бин без деформаций (ветки разреза)
        p_cont = self.parent_cont
        childe = self.children.children.children
        size = childe.bin.size
        last_rolldir = childe.bin.last_rolldir
        if last_rolldir == Direction.H:
            width = size[WIDTH] * size[HEIGHT] / self.bin.height
        else:
            length = size[LENGTH] * size[HEIGHT] / self.bin.height
        parent_bin = p_cont.bin
        if self.parent.direction == Direction.H:
            width = parent_bin.width
            adj_width = width
            adj_length = parent_bin.length - length
        else:
            length = parent_bin.length
            adj_width = parent_bin.width - width
            adj_length = length
        bin_ = Bin(
            length, width, self.bin.height,
            parent_bin.last_rolldir, self.bin.material, self.bin.bin_type
        )
        self.bin = bin_
        adj_node = self.parent.children[0]
        bin_ = Bin(
            adj_length, adj_width, adj_node.bin.height,
            adj_node.bin.last_rolldir, adj_node.bin.material,
            adj_node.bin.bin_type
        )
        adj_node.bin = bin_
        self.update_size(max_len=kwargs.get('max_len'))

    def fix_sizes(self, width, length, is_min=False, miss_bins=False,
                  max_len=None, max_size=None, restrictions=None):
        # Лучше разнести этот метод по разным классам
        p_cont = self.parent_cont
        if not is_ubin_node(self):
            if miss_bins:
                p_cont.fix_sizes(
                    self.bin.width, self.bin.length, is_min=is_min,
                    miss_bins=miss_bins, max_size=max_size,
                    restrictions=restrictions
                )
            return
        troot = self.get_troot()
        if is_ubin_node(p_cont):
            height = p_cont.bin.d_height
        else:
            height = p_cont.bin.height
        if is_ubin_node(troot) and troot.bin.bin_type == BinType.INTERMEDIATE:
            pass
        elif is_ubin_node(troot) and self.in_right_branch():
            return
        if width == 0 or length == 0:
            return
        last_deformations = [item for _, item in self.bin.last_deformations()]
        last_rolldir = last_deformations[-1]
        # если потомок упаковка (то фиксируем без всего)
        if self.children and is_packing_node(self.children):
            self._fix_semifinished(
                width, length, max_size=max_size, is_min=is_min,
                miss_bins=miss_bins, max_len=max_len,
                restrictions=restrictions
            )
        elif len(last_deformations) == 2:
            # print('Фиксация бина с двумя деформациями')
            if is_cutting_node(self.parent):
                neighbour = [is_bin_node(node.children) for node in self.children.list_of_children()]
                if not all(neighbour):
                    return
                if is_rolling_node(self.children):
                    if len(self.children.list_of_children()) == 2:
                        left, right = self.children.children
                        max_size_ = [(), max_size] if self.bin.d_height > 3 else [max_size, ()]
                        delete_all_branch(left, max_size_, without_root=False)
                        delete_all_branch(right, max_size_, without_root=False)
                        if len(self.children.list_of_children()) == 2:
                            left_cc = left.cc_leaves[0]
                            right_cc = right.cc_leaves[0]
                            left_ef = left_cc.result.total_efficiency(*left_cc.parent_bnode.bin.size[:2])
                            right_ef = right_cc.result.total_efficiency(*right_cc.parent_bnode.bin.size[:2])
                            left_ef *= left_cc.result.qty() / self.kit.qty()
                            right_ef *= right_cc.result.qty() / self.kit.qty()
                            length, width, _ = right.estimate_size()
                            right_dist = self.bin.estimator(width, length, last_deformations)
                            if right_ef >= left_ef and right_dist is not None:
                                self.children.delete(left)
                            else:
                                self.children.delete(right)
                        
                estimate = self.estimate_size()
                width = estimate[WIDTH]
                length = estimate[LENGTH]
                # FIXME: косяк, если объединенная оценка выходит за границы,
                # для подветок маленьких примеров (example_9)
                dist = self.bin.estimator(width, length, last_deformations)
                if dist is None:
                    dist = (0, 0)
                if last_rolldir == Direction.H:
                    width += dist[0]
                else:
                    length += dist[1]
                bin_ = Bin(
                    length, width, self.bin.d_height,
                    last_rolldir, self.bin.material, self.bin.bin_type
                )
                self.bin = bin_
                anj_node = self.parent.children[0]
                adj_bin = anj_node.bin
                bin_ = Bin(
                    adj_bin.length, adj_bin.width, self.bin.height,
                    last_rolldir, self.bin.material, adj_bin.bin_type
                )
                anj_node.bin = bin_
                self.cc_leaves[0].transfer_size()
                cc_leaves = [
                    node for node in anj_node.template_leaves(anj_node)
                    if is_cc_node(node)
                ]
                for childe in cc_leaves:
                    childe.parent_cont.fix_sizes(
                        childe.bin.width, childe.bin.length, is_min=is_min,
                        miss_bins=True, restrictions=restrictions
                    )
                p_cont.fix_sizes(
                    width, length, is_min=is_min, max_size=max_size,
                    restrictions=restrictions
                )
            elif is_ubin_node(self) and self.bin.bin_type == BinType.INTERMEDIATE:
                size = self.estimate_size()
                used_width = max(self.bin.width, size[WIDTH])
                used_length = max(self.bin.length, size[LENGTH])
                dist = self.bin.estimator(used_width, used_length, last_deformations)
                if last_rolldir == Direction.H:
                    width = dist[0] + used_width
                    length = used_length
                else:
                    length = dist[1] + used_length
                    width = used_width
                bin_ = Bin(
                    length, width, self.bin.d_height,
                    last_rolldir, self.bin.material, self.bin.bin_type
                )
                self.bin = bin_
                p_cont.fix_sizes(
                    width, length, is_min=is_min, max_size=max_size,
                    restrictions=restrictions
                )
            else:
                dist = self.bin.estimator(width, length, last_deformations)
                last_rolldir = last_deformations[-1]
                height = self.bin.d_height
                if last_rolldir == Direction.H:
                    width += dist[0]
                else:
                    length += dist[1]
                bin_ = Bin(
                    length, width, height,
                    last_rolldir, self.bin.material, self.bin.bin_type
                )
                self.bin = bin_
                anj_node = self.children.children[0]
                adj_bin = anj_node.bin
                bin_ = Bin(
                    adj_bin.length, adj_bin.width, height,
                    last_rolldir, self.bin.material, adj_bin.bin_type
                )
                anj_node.bin = bin_
                self.cc_leaves[0].transfer_size()
                cc_leaves = [
                    node for node in anj_node.template_leaves(anj_node)
                    if is_cc_node(node)
                ]
                for childe in cc_leaves:
                    childe.parent_cont.fix_sizes(
                        childe.bin.width, childe.bin.length, is_min=is_min,
                        miss_bins=True, restrictions=restrictions
                    )
                parent = self.get_parent_ubin()
                parent.fix_sizes(
                    width, length, is_min=is_min, max_size=max_size,
                    restrictions=restrictions
                )
        elif len(last_deformations) == 1:
            # print('Фиксация бина с одной деф')
            if p_cont is not troot and is_ubin_node(p_cont):
                current_height = (p_cont.bin.d_height - self.bin.d_height) / 2 + self.bin.d_height
                if last_rolldir == Direction.H:
                    if max_size:
                        new_length = max_size[WIDTH]
                        if length >= new_length:
                            current_height = length * self.bin.d_height / new_length
                            alternative_height = p_cont.bin.width * p_cont.bin.d_height / width
                            if current_height > p_cont.bin.d_height:
                                current_height = p_cont.bin.d_height
                            elif alternative_height > current_height:
                                current_height = alternative_height
                    length = length * self.bin.d_height / current_height
                else:
                    if max_size:
                        new_width = max_size[WIDTH]
                        if width >= new_width:
                            current_height = width * self.bin.d_height / new_width
                            alternative_height = p_cont.bin.length * p_cont.bin.d_height / length
                            if current_height > p_cont.bin.d_height:
                                current_height = p_cont.bin.d_height
                            elif alternative_height > current_height:
                                current_height = alternative_height
                    width = width * self.bin.d_height / current_height
                bin_ = Bin(
                    length, width, current_height,
                    last_rolldir, self.bin.material, self.bin.bin_type
                )
                self.bin = bin_
                if last_rolldir == Direction.H:
                    width = width * current_height / p_cont.bin.d_height
                else:
                    length = length * current_height / p_cont.bin.d_height
                p_cont.fix_sizes(
                    width, length, is_min=is_min, max_size=max_size,
                    restrictions=restrictions
                )
                return
            elif is_ubin_node(self) and self.bin.bin_type == BinType.INTERMEDIATE:
                childe = self.children.children
                if childe.bin.rolldir == Direction.H:
                    current_height = width * childe.bin.height / p_cont.bin.width
                    width = p_cont.bin.width
                else:
                    current_height = length * childe.bin.height / p_cont.bin.length
                    length = p_cont.bin.length
                bin_ = Bin(
                    length, width, current_height,
                    last_rolldir, self.bin.material, self.bin.bin_type
                )
                self.bin = bin_
                p_cont.fix_sizes(
                    width, length, is_min=is_min, max_size=max_size,
                    restrictions=restrictions
                )
            elif is_ubin_node(troot) and is_imt_node(troot):
                self._fix_intermediate(
                    width, length, max_size=max_size, is_min=is_min,
                    miss_bins=miss_bins, max_len=max_len,
                    restrictions=restrictions
                )
            elif not is_ubin_node(p_cont) or self.in_right_branch():
                childe = self.children.children
                if p_cont.bin.bin_type in (BinType.leaf, BinType.adjacent):
                # if p_cont.bin.bin_type == BinType.leaf:
                    # устанавливаем минимальные размеры (у себя и у предка!!!)
                    if last_rolldir == Direction.H:
                        if length > p_cont.bin.length and width > p_cont.bin.width:
                            # current_height = p_cont.bin.width * height / width
                            # length = round(length * current_height / height, 4)
                            if max_size and length > max_size[WIDTH]:
                                current_height = p_cont.bin.width * height / width
                                length = length * self.bin.d_height / current_height
                            else:
                                current_height = p_cont.bin.width * height / width
                                length = round(length * current_height / height, 4)
                        elif length > p_cont.bin.length and width <= p_cont.bin.width:
                            current_height = length * self.bin.d_height / p_cont.bin.length
                            length = p_cont.bin.length
                        elif length <= p_cont.bin.length and width > p_cont.bin.width:
                            current_height = p_cont.bin.width * height / width
                            length = round(length * current_height / height, 4)
                        else:
                            current_height = height
                            length = round(length * self.bin.d_height / height, 4)

                        is_locked = to_delete(length, width, max_size)
                    else:
                        if length > p_cont.bin.length and width > p_cont.bin.width:
                            # current_height = p_cont.bin.length * height / length
                            if max_size and length > max_size[WIDTH]:
                                # current_height = p_cont.bin.width * height / width
                                current_height = p_cont.bin.width * height / width
                                length = length * self.bin.d_height / current_height
                            else:
                                current_height = p_cont.bin.length * height / length
                                width = width * self.bin.d_height / current_height
                        elif length > p_cont.bin.length and width <= p_cont.bin.width:
                            current_height = p_cont.bin.length * height / length
                            width = width * self.bin.d_height / current_height
                        elif length <= p_cont.bin.length and width > p_cont.bin.width:
                            # current_height = width * self.bin.d_height / p_cont.bin.width
                            current_height = p_cont.bin.height
                            # width = p_cont.bin.width
                            width = width * self.bin.d_height / p_cont.bin.height
                        else:
                            current_height = height
                            width = round(width * self.bin.d_height / height, 4)

                        is_locked = to_delete(width, length, max_size)

                    self.locked = is_locked  # для отладки
                else:
                    # здесь фиксируются бины между промежуточным и корнем
                    if last_rolldir == Direction.H:
                        length = p_cont.bin.length
                        max_width = p_cont.bin.width
                        if max_size:
                            max_width = max(max_size[WIDTH], p_cont.bin.width)
                        if max_size and width > max_width:
                            current_height = p_cont.bin.width * p_cont.bin.height / max_width
                        else:
                            current_height = p_cont.bin.width * p_cont.bin.height / width
                    else:
                        width = p_cont.bin.width
                        max_length = p_cont.bin.length
                        if max_size:
                            max_length = max(max_size[WIDTH], p_cont.bin.length)
                        if max_size and length > max_length:
                            current_height = p_cont.bin.length * p_cont.bin.height / max_length
                        else:
                            current_height = p_cont.bin.length * p_cont.bin.height / length
                bin_ = Bin(
                    length, width, current_height,
                    last_rolldir, self.bin.material, self.bin.bin_type
                )
                self.bin = bin_
                p_cont.fix_sizes(
                    width, length, is_min=is_min, max_size=max_size,
                    restrictions=restrictions
                )
        else:
            self._fix_node_withot_def(
                width, length, max_size=max_size, is_min=is_min,
                miss_bins=miss_bins, max_len=max_len,
                restrictions=restrictions
            )

    def update_kit(self, height):
        self.kit.delete_height(height)
        return super().update_kit(height=height)

    def get_parent_ubin(self):
        if self.parent is None:
            return None
        if self.parent.parent is None:
            return None
        if is_ubin_node(self.parent.parent):
            return self.parent.parent

    def is_troot(self):
        return is_adj_node(self)

    def __copy__(self):
        return self.__class__(bin=copy(self.bin), kit=copy(self.kit))

    def __repr__(self):
        return f'{self.__class__.__name__}({self.bin}, {self.kit})'


class OperationNode(Node):
    def __init__(self, operation, children=None, parent=None) -> None:
        super().__init__(children=children, parent=parent)
        self.operation = operation
        self.direction = None
        self.point = None  # длина, ширина

    def create(self, height, *args, **kwargs):
        parent_height = self.parent_bnode.bin.height
        if height > parent_height:
            msg = (
                'Невозможно создать потомков с большей толщиной '
                f'({height}) чем у предка ({parent_height})'
            )
            raise SizeError(msg)
        if self.parent is None:
            raise ParentNodeError(f'Узел {self} не имеет предка')
        create_nodes_rolling = partial(self._create_nodes_rolling, height)
        create_nodes_cutting = partial(self._create_nodes_cutting, height)
        operations_spawn_func = {
            Operations.rolling.name: create_nodes_rolling,
            Operations.v_rolling.name: create_nodes_rolling,
            Operations.h_rolling.name: create_nodes_rolling,
            Operations.cutting.name: create_nodes_cutting,
            Operations.packing.name: self._create_nodes_packing,
        }
        spawn_func = operations_spawn_func[self.operation.name]
        node = spawn_func(**kwargs)

        return node

    def _create_nodes_rolling(self, rolled_height, double_sided=True, **kwargs):
        """Создание потомков при прокате"""
        if self.operation == Operations.rolling:
            vertical = OperationNode(Operations.v_rolling)
            horizontal = OperationNode(Operations.h_rolling)
            return vertical, horizontal
            # return OperationNode(Operations.v_rolling)
            # if is_op_node(pparent) and pparent.operation == Operations.cutting:
            #     return OperationNode(Operations.v_rolling)
            # создание двух узлов с разными направлениями
        # создание одного бина с модифицированными размерами
        parent_bn = self.parent_bnode
        if parent_bn is None:
            raise ParentNodeError(f'Узел {self} не имеет предка')
        size: Vec3 = parent_bn.bin.size  # length, width, height

        if self.operation == Operations.v_rolling:
            if not double_sided:
                new_length = deformation(
                    size[LENGTH], size[HEIGHT], rolled_height
                )
                size = new_length, size[WIDTH], rolled_height
            rolldir = Direction.V
        else:
            if not double_sided:
                new_width = deformation(
                    size[WIDTH], size[HEIGHT], rolled_height
                )
                size = size[LENGTH], new_width, rolled_height
            rolldir = Direction.H
        bin_type = BinType.leaf

        parent_cont = self
        while parent_cont.parent is not None and not is_cutting_node(parent_cont.parent):
            parent_cont = parent_cont.parent
        parent_bn = parent_cont

        if parent_bn and parent_bn.bin.bin_type == BinType.leaf:
            if parent_bn.parent and is_op_node(parent_bn.parent):
                if parent_bn.parent.operation == Operations.cutting:
                    if is_ubin_node(self.parent):
                        bin_type = BinType.semifinished

        cut_thickness = kwargs.get('cut_thickness')
        if is_ubin_node(self.parent_cont):
            height = self.parent_cont.bin.d_height
        else:
            height = parent_bn.bin.height
        is_intermediate = bool(cut_thickness)

        max_h = max(self.parent_bnode.kit.blanks.keys())
        if is_intermediate and not is_op_node(self.parent) and max_h != cut_thickness:
            bin_type = BinType.INTERMEDIATE

        if double_sided:
            parent_bn = self.parent_cont
            bin_ = UnsizedBin(
                *size, rolled_height,
                material=parent_bn.bin.material, bin_type=bin_type
            )
            if is_ubin_node(parent_bn):
                for d in parent_bn.bin.deformations:
                    bin_.add_deformation(d)
            bin_.add_deformation((rolled_height, rolldir))
        else:
            bin_ = Bin(
                *size, rolldir=rolldir,
                material=parent_bn.bin.material, bin_type=bin_type
            )
        # при прокате набор заготовок наследуется без изменений
        return BinNode(bin_, kit=deepcopy(parent_bn.kit))

    def _create_nodes_cutting(self, height, **kwargs):
        """Создание потомков при разрезе"""
        parent_bn = self.parent
        if parent_bn is None:
            raise ParentNodeError(f'Узел {self} не имеет предка')
        bin_ = self.parent_cont.bin
        kit = self.parent_cont.kit
        # if height not in kit:
        #     raise KitError(f'Набор {kit} не содержит толщину {height}')
        if is_ubin_node(parent_bn):
            BinClass = UnsizedBin
            if isinstance(bin_, UnsizedBin):
                bin_height = bin_.d_height
            else:
                bin_height = height
            args = (bin_height, )
            deformations = parent_bn.bin.deformations
        else:
            BinClass = Bin
            args = ()
            deformations = None
        contiguous_bin = BinClass(
            0., 0., bin_.height, *args, rolldir=bin_.rolldir,
            material=bin_.material, bin_type=BinType.adjacent
        )
        if self.parent.bin.bin_type == BinType.leaf:
            bin_type = BinType.semifinished
        else:
            bin_type = BinType.leaf
        leaf_bin = BinClass(
            *bin_.size, *args, rolldir=bin_.rolldir,
            material=bin_.material, bin_type=bin_type
        )

        if deformations:
            for d in deformations:
                contiguous_bin.add_deformation(d)
                leaf_bin.add_deformation(d)

        right_kit, left_kit = kit.separate(height)
        left = BinNode(contiguous_bin, kit=left_kit)
        right = BinNode(leaf_bin, kit=right_kit)
        return left, right

    def _create_nodes_packing(self, **kwargs):
        """Создание потомков при упаковке"""
        return CuttingChartNode(self.parent.bin)

    # работа с размерами (оценка, обновление) --------------------------
    def estimate_size(self, *, start=None):
        estimate = super().estimate_size(start=start)
        parent_bin = self.parent_cont.bin
        if is_ubin_node(self.parent_cont):
            height = parent_bin.d_height
        else:
            height = parent_bin.height
        if self.operation == Operations.cutting:
            if self.direction is None:
                return (0, 0, height)
            if len(estimate) == 2:
                left, right = estimate
                if self.direction == Direction.H:
                    # горизонтальный разрез - макс ширина, сумма длин
                    length = left[LENGTH] + right[LENGTH]
                    width = max(left[WIDTH], right[WIDTH])
                else:
                    # вертикальный разрез - макс длина, сумма ширин
                    length = max(left[LENGTH], right[LENGTH])
                    width = left[WIDTH] + right[WIDTH]
                estimate = length, width, height
        elif self.operation == Operations.rolling:
            if len(self.list_of_children()) == 2:
                length = max(est[LENGTH] for est in estimate)
                width = max(est[WIDTH] for est in estimate)
                estimate = length, width, height
        elif self.operation == Operations.v_rolling:
            length = deformation(
                estimate[LENGTH], estimate[HEIGHT],
                height, parent_bin.material.extension
            )
            estimate = length, estimate[WIDTH], height
        elif self.operation == Operations.h_rolling:
            width = deformation(
                estimate[WIDTH], estimate[HEIGHT],
                height, parent_bin.material.extension
            )
            estimate = estimate[LENGTH], width, height
        return estimate

    def update_size(self, *, start=None, max_len=None):
        if self.parent_bnode is None:
            return
        parent_size = self.parent_bnode.bin.size
        if self.operation == Operations.cutting:
            if self.direction is None:
                # установить разрез
                self.set_cut(max_len=max_len)
            else:
                # обновить разрез
                self.update_cut()
            left, right = self.children
            if self.direction == Direction.H:
                right.bin.length = self.point[LENGTH]
                left.bin.length = parent_size[LENGTH] - self.point[LENGTH]
                left.bin.width = parent_size[WIDTH]
                # left.bin.width = self.point[WIDTH]
                right.bin.width = parent_size[WIDTH]
            else:
                right.bin.width = self.point[WIDTH]
                right.bin.length = parent_size[LENGTH]
                # right.bin.length = self.point[LENGTH]
                left.bin.length = parent_size[LENGTH]
                left.bin.width = parent_size[WIDTH] - self.point[WIDTH]
            if is_ubin_node(right):
                right.bin.height = parent_size[HEIGHT]
            if is_ubin_node(left):
                left.bin.height = parent_size[HEIGHT]
        elif self.operation == Operations.h_rolling:
            childe_bin = self.children.bin
            if is_ubin_node(self.children):
                childe_bin.height = parent_size[HEIGHT]
            childe_bin.length = parent_size[LENGTH]
            childe_bin.width = deformation(
                parent_size[WIDTH], parent_size[HEIGHT],
                childe_bin.height, childe_bin.material.extension
            )
        elif self.operation == Operations.v_rolling:
            childe_bin = self.children.bin
            if is_ubin_node(self.children):
                childe_bin.height = parent_size[HEIGHT]
            childe_bin.width = parent_size[WIDTH]
            childe_bin.length = deformation(
                parent_size[LENGTH], parent_size[HEIGHT],
                childe_bin.height, childe_bin.material.extension
            )
        return super().update_size(start=start, max_len=max_len)

    def transfer_size(self, to_right=False, max_len=None):
        if self.operation != Operations.cutting:
            msg = (
                f'The node type "{self.operation.value}"'
                ' cannot the transfer sizes'
            )
            raise OperationTypeError(msg)
        left, right = self.children
        size = self.parent_bnode.bin.size
        if to_right:
            src, dst = left, right
        else:
            src, dst = right, left
        estimate = src.estimate_size()
        if estimate[LENGTH] == 0 or estimate[WIDTH] == 0:
            src.bin.length = 0.
            src.bin.width = 0.
            dst.bin.length = size[LENGTH]
            dst.bin.width = size[WIDTH]
        else:
            if is_ubin_node(self.children[0]):
                used_volume = estimate[0] * estimate[1] * estimate[2]
                free_volume = self.children[0].bin.volume - used_volume
                length, width = 50, 50
                height = free_volume / (length * width)
                dst.bin.length = length
                dst.bin.width = width
                dst.bin.height = height
            else:
                # перенос только по разрезу
                if self.direction is None:
                    self.set_cut(max_len)
                    # msg = (
                    #     f'Узел {self} не имеет разреза. '
                    #     'Размеры не могут быть перенесены'
                    # )
                    # raise OperationNodeError(msg)
                if self.direction == Direction.H:
                    src.bin.length = estimate[LENGTH]
                    dst.bin.length = size[LENGTH] - estimate[LENGTH]
                    dst.bin.width = size[WIDTH]
                    self.point = right.bin.length, 0.
                else:
                    src.bin.width = estimate[WIDTH]
                    dst.bin.width = size[WIDTH] - estimate[WIDTH]
                    dst.bin.length = size[LENGTH]
                    self.point = 0., right.bin.width
            src.update_size(max_len=max_len)
            dst.update_size(max_len=max_len)

    def set_cut(self, max_len=None):
        if self.operation == Operations.cutting:
            is_left = False
            parent_size = self.parent_bnode.bin.size
            left, right = self.children
            estimate = right.estimate_size()
            if estimate[LENGTH] == 0 or estimate[WIDTH] == 0:
                estimate = left.estimate_size()
                is_left = True
            s_1 = parent_size[WIDTH] * (parent_size[LENGTH] - estimate[LENGTH])
            s_2 = parent_size[LENGTH] * (parent_size[WIDTH] - estimate[WIDTH])
            if max_len:
                # Сравнивать с max_len
                if parent_size[WIDTH] <= max_len and parent_size[LENGTH] <= max_len:
                    # можем выбирать
                    max_side = max(parent_size[LENGTH], parent_size[WIDTH])
                    min_side = min(parent_size[LENGTH], parent_size[WIDTH])
                    if max_side / min_side > 2:
                        if parent_size[LENGTH] > parent_size[WIDTH]:
                            self.direction = Direction.H
                            if is_left:
                                self.point = (parent_size[LENGTH] - estimate[LENGTH], 0.)
                            else:
                                self.point = (estimate[LENGTH], 0.)
                        else:
                            self.direction = Direction.V
                            if is_left:
                                self.point = (0., parent_size[WIDTH] - estimate[WIDTH])
                            else:
                                self.point = (0., estimate[WIDTH])
                    elif s_1 >= s_2:
                        self.direction = Direction.H
                        if is_left:
                            self.point = (parent_size[LENGTH] - estimate[LENGTH], 0.)
                        else:
                            self.point = (estimate[LENGTH], 0.)
                    else:
                        self.direction = Direction.V
                        if is_left:
                            self.point = (0., parent_size[WIDTH] - estimate[WIDTH])
                        else:
                            self.point = (0., estimate[WIDTH])
                elif parent_size[WIDTH] <= max_len:
                    # только горизонтальный
                    self.direction = Direction.H
                    if is_left:
                        self.point = (parent_size[LENGTH] - estimate[LENGTH], 0.)
                    else:
                        self.point = (estimate[LENGTH], 0.)
                elif parent_size[LENGTH] <= max_len:
                    # только вертикальный
                    self.direction = Direction.V
                    if is_left:
                        self.point = (0., parent_size[WIDTH] - estimate[WIDTH])
                    else:
                        self.point = (0., estimate[WIDTH])
                else:
                    raise SizeError('Невозможно разрезать лист')
            else:
                if abs(s_1) >= abs(s_2):
                # if s_1 >= s_2:
                    self.direction = Direction.H
                    if is_left:
                        self.point = (parent_size[LENGTH] - estimate[LENGTH], 0.)
                    else:
                        self.point = (estimate[LENGTH], 0.)
                else:
                    self.direction = Direction.V
                    if is_left:
                        self.point = (0., parent_size[WIDTH] - estimate[WIDTH])
                    else:
                        self.point = (0., estimate[WIDTH])
        else:
            msg = ('Операция установки направления разреза доступна только '
                   'для узлов разреза')
            raise OperationTypeError(msg)

    def update_cut(self):
        if self.operation != Operations.cutting:
            msg = 'Разрез доступен только для узлов разреза'
            raise OperationTypeError(msg)
        _, right = self.children
        right_size = right.estimate_size()
        if self.direction == Direction.H:
            self.point = right_size[LENGTH], 0.
        else:
            self.point = 0., right_size[WIDTH]

    @property
    def last_rolldir(self):
        if self.operation == Operations.h_rolling:
            return Direction.H
        if self.operation == Operations.v_rolling:
            return Direction.V
        return super().last_rolldir

    @property
    def name(self):
        return self.operation.value

    def __copy__(self):
        obj = self.__class__(self.operation)
        obj.direction = self.direction
        obj.point = self.point
        return obj

    def __repr__(self):
        return f'{self.__class__.__name__}({self.operation})'


class CuttingChartNode(Node):
    def __init__(self, bin: Bin, children=None, parent=None) -> None:
        super().__init__(children=children, parent=parent)
        self.bin = bin
        if isinstance(self.bin, UnsizedBin):
            height = self.bin.d_height
        else:
            height = self.bin.height
        self.result = Result({}, [], 0., 0, height)
        self.hem = (0, 0)

    def pack(self, sorting='width', max_size=None, restrictions=None):
        # if not self.size_check():
        #     self.kit.delete_height(self.bin.height)
        #     return self.result
        # bin_node = self.parent_bnode
        bin_node = self.parent.parent
        if bin_node is None:
            msg = 'The packing node has no parent with container'
            raise ParentNodeError(msg)
        if bin_node.kit is None:
            msg = (
                f'The bin node {bin_node} does not '
                'contain a set of rectangles.'
            )
            raise KitError(msg)
        bin_node.kit.sort(sorting)
        cutting_node, _ = self.parent_cnode()
        if cutting_node.direction == Direction.H:
            x_0, y_0 = 0, self.result.length
        else:
            x_0, y_0 = self.result.width, 0

        if isinstance(self.bin, UnsizedBin):
            height = self.bin.d_height
            length = self.bin.estimator.max_length
            width = self.bin.estimator.max_width
        else:
            height = self.bin.height
            length = self.bin.length
            width = self.bin.width
        if restrictions:
            if height <= 3:
                hem = restrictions.get('hem_after_3')
            else:
                hem = restrictions.get('hem_until_3')
            end = restrictions.get('end', 0)
            allowance = restrictions.get('allowance', 0)
        else:
            hem = end = allowance = 0
        if self.bin.rolldir == Direction.H:
            # ширина, длина
            self.hem = (hem, 0)
            self.y_hem = (hem, hem)
            x_hem = end * length if end * length <= 30 else 30
            if bin_node.parent.direction == Direction.H:
                self.x_hem = (x_hem, 0)
            else:
                self.x_hem = (x_hem, x_hem)
        else:
            self.hem = (0, hem)
            self.x_hem = (hem, hem)
            y_hem = end * width if end * width <= 30 else 30
            if bin_node.parent.direction == Direction.H:
                self.y_hem = (y_hem, 0)
            else:
                self.y_hem = (y_hem, y_hem)

        if isinstance(self.bin, UnsizedBin):
            bin_node.kit.rotate(self.bin.d_height, self.bin.rolldir)
            group = bin_node.kit[self.bin.d_height]
            _, main_region, min_rect, result, unplaced, tailings = bpp_ts(
                bin_node.bin.length, bin_node.bin.width, bin_node.bin.height,
                bin_node.bin.d_height, group, self.bin.rolldir, x_hem=self.x_hem, y_hem=self.y_hem,
                allowance=allowance, max_size=max_size,
                is_visualize=False
            )
            width, length = min_rect.width, min_rect.length
            self.bin = Bin(
                length, width, bin_node.bin.d_height,
                self.bin.last_rolldir, self.bin.material, self.bin.bin_type
            )
            self.result.update(result, tailings=tailings, unplaced=unplaced)
            bin_node.fix_sizes(
                width, length, max_size=max_size, restrictions=restrictions
            )
        else:
            length, width, _ = self.available_size()
            group = bin_node.kit[self.bin.height]
            if not self.size_check():
                for k in group:
                    group[k] = []
                return
            result, *_ = ph_bpp(
                length, width, group, x0=x_0, y0=y_0, first_priority=True
            )
            self.result.update(result, tailings=None)

        if self.result.is_empty:
            troot = self.get_troot()
            troot.kit.delete_height(self.bin.d_height)
            self.delete_branch()


        return self.result

    # работа с размерами (оценка, обновление) --------------------------
    def estimate_size(self, *, start=None):
        if start is not None:
            # вызов из других узлов
            return self.result.length, self.result.width, self.bin.height
        # вызов из текущего узла
        cutting_node, leaf_node = self.parent_cnode()
        contiguous_node = [
            o for o in cutting_node.children if o is not leaf_node
        ]
        if contiguous_node:
            contiguous_node = contiguous_node[0]
        else:
            msg = 'The cut node does not have enough children'
            raise ChildrenNodeError(msg)
        return contiguous_node.estimate_size(start=None)

    def update_size(self, *, start=None, max_len=None):
        if start is None:
            cutting_node, _ = self.parent_cnode()
            if cutting_node is None:
                return
            cutting_node.update_size(start=self, max_len=max_len)
        if self.parent_bnode is None:
            return
        parent_size = self.parent_bnode.bin.size
        self.bin.length = parent_size[LENGTH]
        self.bin.width = parent_size[WIDTH]
        return super().update_size(start=start, max_len=max_len)

    def transfer_size(self, to_right=False):
        cutting_node, _ = self.parent_cnode()
        cutting_node.transfer_size(to_right=to_right)

    def available_size(self, *, start=None):
        cutting_node, _ = self.parent_cnode()
        estimate = cutting_node.estimate_size()
        if estimate[LENGTH] == 0 or estimate[WIDTH] == 0:
            length, width, height = cutting_node.parent_bnode.bin.size
            if self.bin.height != height:
                if self.last_rolldir == Direction.H:
                    width = deformation(
                        width, height, self.bin.height,
                        self.bin.material.extension
                    )
                else:
                    length = deformation(
                        length, height, self.bin.height,
                        self.bin.material.extension
                    )
            esize = self.e_size()
            if esize[WIDTH] == width:
                length -= esize[LENGTH]
            else:
                width -= esize[WIDTH]
            return length, width, self.bin.height
        estimate = self.parent.estimate_size()
        if self.parent.direction == Direction.H:
            size = (
                self.parent_bnode.bin.length - estimate[LENGTH],
                self.parent_bnode.bin.width,
                self.bin.height,
            )
        else:
            size = (
                self.parent_bnode.bin.length,
                self.parent_bnode.bin.width - estimate[WIDTH],
                self.bin.height,
            )
        return size

    def size_check(self):
        if isinstance(self.bin, UnsizedBin):
            height = self.bin.d_height
        else:
            height = self.bin.height
        blanks = self.kit.unplaced(self.bin, height)
        dst = self.available_size()
        for item in blanks:
            if is_subrectangle(item.size, dst, with_rotate=item.is_rotatable):
                return True
        return False

    def e_size(self):
        if self.result.length == 0.:
            return 0., 0.
        s_1 = self.bin.width * (self.bin.length - self.result.length)
        s_2 = self.bin.length * (self.bin.width - self.result.width)
        if s_1 >= s_2:
            return self.result.length, self.bin.width, self.bin.height
        return self.bin.length, self.result.width, self.bin.height

    def parent_cnode(self):
        parent = self.parent
        child = self
        def is_cnode(node):
            return is_op_node(node) and node.operation == Operations.cutting
        while parent is not None and not is_cnode(parent):
            child = parent
            parent = parent.parent
        return parent, child

    @property
    def kit(self):
        if self.parent.parent:
            return self.parent.parent.kit
        return None

    def __copy__(self):
        obj = self.__class__(copy(self.bin))
        obj.result = copy(self.result)
        return obj


class Tree:
    def __init__(self, root: BinNode) -> None:
        self.root = root

    @staticmethod
    def create_template(parent: BinNode, height, cut_thickness=None):
        nodes = deque([parent])
        parent_children = []
        while nodes:
            node = nodes.popleft()
            if node is not parent:
                is_ubin_or_bin = is_ubin_node(node) or is_bin_node(node)
                if is_ubin_or_bin and node.bin.bin_type in (BinType.adjacent, BinType.INTERMEDIATE):
                    continue
                if is_cc_node(node):
                    continue
            children = node.create(height, cut_thickness=cut_thickness)
            if node is parent:
                parent_children = children
                parent.set_parent(children)
            else:
                node.children = children
            if isinstance(children, Iterable):
                nodes.extend(children)
            else:
                nodes.append(children)
        return parent_children

    def create_template_branches(self, parent: BinNode, height, cut_thickness=None):
        children = self.__class__.create_template(parent, height, cut_thickness=cut_thickness)
        if not isinstance(children, (list, tuple)):
            children = [children]
        trees = []
        for childe in children:
            branches = all_branches(childe)
            for i, branch in enumerate(branches):
                new_tree = deepcopy(self)
                new_parent = new_tree.node_by_id(parent._id)
                trees.append((new_tree, new_parent, branch))
        return trees

    def node_by_id(self, id_):
        for node in dfs(self.root):
            if node._id == id_:
                return node
        return None


def all_branches(root):
    branches = []
    if not root.cc_leaves:
        leaves = root.adj_leaves
    else:
        leaves = root.cc_leaves
    for node in leaves:
        path = []
        while node:
            if is_op_node(node) and node.operation == Operations.cutting:
                children = node.list_of_children()
                if len(children) == 2:
                    left, _ = children
                    path.append(left)
            path.append(node)
            node = node.parent
        branches.append(copy_tree(root, path))
    return branches


def all_solutions(tree):
    root = tree.root
    all_paths = []
    for node in root.adj_leaves:
        nodes = [[]]
        while node:
            if is_op_node(node) and node.operation == Operations.cutting:
                children = [
                    n for n in node.list_of_children() if n not in [o[-1] for o in nodes]
                ]
                for childe in children:
                    paths = top_down_traversal(childe)
                    nodes = [
                        list(chain.from_iterable(item)) for item in product(nodes, paths)
                    ]
            for path in nodes:
                path.append(node)
            node = node.parent
        all_paths.extend(nodes)
    return all_paths


def top_down_traversal(start):
    paths = [[start]]
    result = []
    while paths:
        path = paths[0]
        node = path[-1]
        children = node.list_of_children()
        if children:
            for i, childe in enumerate(children):
                if i == 0:
                    path.append(childe)
                else:
                    paths.append(list(path[:-1]))
                    paths[-1].append(childe)
        else:
            result.append(paths.pop(0))
    return result


def solution_efficiency(root, path, nd=False, is_total=False, is_p=False):
    # is_total - Учитывая весь бин
    # nd - взвешенная на количество деталей
    used_total_volume = 0.
    used_volume = 0.
    number_detail = 0
    priorities = []
    all_priorities = []
    for node in path:
        if is_cc_node(node):
            used_total_volume += node.bin.volume
            used_volume += node.result.total_volume
            priorities.extend([1/blank.rectangle.priority for blank in node.result])
            all_priorities.extend([1/blank.rectangle.priority for blank in node.result])
            all_priorities.extend([1/blank.priority for blank in node.result.unplaced])
            number_detail += node.result.qty()
    if is_total:
        efficiency = used_volume / root.bin.volume
    else:
        if used_total_volume == 0:
            efficiency = 0
        else:
            efficiency = used_volume / used_total_volume
    if len(set(all_priorities)) == 1:
        if nd and number_detail:
            efficiency *= number_detail / root.kit.qty()
    elif is_p:
        sp = sum(all_priorities)
        priorities = [p / sp for p in priorities]
        efficiency = (efficiency + sum(priorities)) / 2
    return efficiency


def optimal_configuration(tree, lower=1., nd=False, is_total=False):
    solutions = all_solutions(tree)
    if lower == 1:
        result =  max(
            solutions,
            key=lambda item: solution_efficiency(item[-1], item[:-1],
                                                 nd=nd, is_total=is_total)
        )
        return solution_efficiency(
            result[-1], result[:-1], nd=nd, is_total=is_total
        ), *copy_tree(tree.root, result)
    result = []
    for item in solutions:
        efficiency = solution_efficiency(
            item[-1], item[:-1], nd=nd, is_total=is_total
        )
        if efficiency >= lower:
            result.append((efficiency, *copy_tree(item[-1], item[:-1])))
    return result


def copy_tree(root, nodes):
    dst_root = copy(root)
    dst_nodes = []
    level = deque([(dst_root, root)])
    while level:
        dst, src = level.popleft()
        for childe in src.list_of_children():
            if childe in nodes:
                new_childe = copy(childe)
                new_childe._id = childe._id
                dst.add(new_childe)
                dst_nodes.append(new_childe)
                level.append((new_childe, childe))
    return dst_root, dst_nodes


def is_bin_node(node) -> bool:
    """Узел является контейнером (фикс. размера)"""
    return isinstance(node, BinNode) and not isinstance(node.bin, UnsizedBin)


def is_ubin_node(node) -> bool:
    """Узел является контейнером (нефикс. размера)"""
    return isinstance(node, BinNode) and isinstance(node.bin, UnsizedBin)


def is_ingot_node(node):
    """Узел является слитком"""
    return is_bin_node(node) and node.bin.bin_type == BinType.ingot


def is_op_node(node) -> bool:
    """Узел является операцией"""
    return isinstance(node, OperationNode)


def is_rolling_node(node):
    """Узел является операцией проката

    В том числе: прокат, горизонтальный прокат, вертикальный прокат.
    """
    return is_op_node(node) and node.operation in (
        Operations.rolling, Operations.h_rolling, Operations.v_rolling
    )


def is_cutting_node(node):
    """Узел является операцией резки"""
    return is_op_node(node) and node.operation == Operations.cutting


def is_packing_node(node):
    """Узел является операцией упаковки"""
    return is_op_node(node) and node.operation == Operations.packing


def is_cc_node(node) -> bool:
    """Узел является схемой раскроя"""
    return isinstance(node, CuttingChartNode)


def is_adj_node(node) -> bool:
    """Узел является корнем шаблона (фикс./нефикс. размеры)

    Корнем шаблона могут быть узлы типа: слиток, смежный остаток,
    промежуточный
    """
    return (
        (is_bin_node(node) or is_ubin_node(node)) and
        node.bin.bin_type in (BinType.adjacent, BinType.ingot,
                              BinType.INTERMEDIATE)
    )


def is_imt_node(node):
    """Узел является промежуточным (фикс./нефикс. размеры)"""
    return (
        (is_bin_node(node) or is_ubin_node(node)) and
        node.bin.bin_type == BinType.INTERMEDIATE
    )


def to_delete(length, width, max_size):
    """Проверка на максимальные размеры"""
    return max_size and (length > max_size[WIDTH] or width > max_size[LENGTH])


def delete_all_branch(root, max_size, without_root=False):
    for node in dfs(root):
        if node not in list(dfs(root)):
            continue
        if without_root and node is root:
            continue
        is_locked = False
        if is_rolling_node(node.parent):
            if node.parent.operation == Operations.h_rolling:
                if max_size:
                    is_locked = to_delete(node.bin.length, node.bin.width, max_size[node.bin.height >= 3])
                is_locked = is_locked and node.bin.height != node.parent_bnode.bin.height
            elif node.parent.operation == Operations.v_rolling:
                if max_size:
                    is_locked = to_delete(node.bin.width, node.bin.length, max_size[node.bin.height >= 3])
                is_locked = is_locked and node.bin.height != node.parent_bnode.bin.height
            if not is_cutting_node(node.parent) and is_locked:
                node.delete_branch()
        elif is_cutting_node(node.parent):
            parent = node.parent
            children = parent.list_of_children()
            if len(children) == 2:
                left_size = children[0].bin.size[:2]
                right_size = children[1].bin.size[:2]
                if parent.direction == Direction.H:
                    if left_size[0] < 0:
                        is_locked = True
                    size = (
                        round(left_size[0] + right_size[0], 4),
                        round(max(left_size[1], right_size[1]), 4)
                    )
                else:
                    if left_size[1] < 0:
                        is_locked = True
                    size = (
                        round(max(left_size[0], right_size[0]), 4),
                        round(left_size[1] + right_size[1], 4)
                    )
            else:
                size = children[0].bin.size[:2]
            parent_bin = parent.parent.bin
            if size[0] > round(parent_bin.size[0], 4) or size[1] > round(parent_bin.size[1], 4):
                is_locked = True
            if is_locked:
                parent.delete_branch()


def to_delete_branch(root, max_size, without_root=False):
    for node in dfs(root):
        if node not in list(dfs(root)):
            continue
        if without_root and node is root:
            continue
        is_locked = False
        if is_rolling_node(node.parent):
            if node.parent.operation == Operations.h_rolling:
                if max_size:
                    is_locked = to_delete(node.bin.length, node.bin.width, max_size[node.bin.height >= 3])
                is_locked = is_locked and node.bin.height != node.parent_bnode.bin.height
            elif node.parent.operation == Operations.v_rolling:
                if max_size:
                    is_locked = to_delete(node.bin.width, node.bin.length, max_size[node.bin.height >= 3])
                is_locked = is_locked and node.bin.height != node.parent_bnode.bin.height
            if not is_cutting_node(node.parent) and is_locked:
                return True
        elif is_cutting_node(node.parent):
            parent = node.parent
            children = parent.list_of_children()
            if len(children) == 2:
                left_size = children[0].bin.size[:2]
                right_size = children[1].bin.size[:2]
                if parent.direction == Direction.H:
                    if left_size[0] < 0:
                        is_locked = True
                    size = (
                        round(left_size[0] + right_size[0], 4),
                        round(max(left_size[1], right_size[1]), 4)
                    )
                else:
                    if left_size[1] < 0:
                        is_locked = True
                    size = (
                        round(max(left_size[0], right_size[0]), 4),
                        round(left_size[1] + right_size[1], 4)
                    )
            else:
                size = children[0].bin.size[:2]
            parent_bin = parent.parent.bin
            if size[0] > round(parent_bin.size[0], 4) or size[1] > round(parent_bin.size[1], 4):
                is_locked = True
            return is_locked
    return False


def is_defective_tree(tree, max_size):
    root = tree.root
    for node in dfs(root):
        if node not in list(dfs(root)):
            continue
        if is_ubin_node(node):
            return False
        is_locked = False
        if is_rolling_node(node.parent):
            if node.parent.operation == Operations.h_rolling:
                if max_size:
                    is_locked = to_delete(node.bin.length, node.bin.width, max_size[node.bin.height >= 3])
                is_locked = is_locked and node.bin.height != node.parent_bnode.bin.height
            elif node.parent.operation == Operations.v_rolling:
                if max_size:
                    is_locked = to_delete(node.bin.width, node.bin.length, max_size[node.bin.height >= 3])
                is_locked = is_locked and node.bin.height != node.parent_bnode.bin.height
            if not is_cutting_node(node.parent) and is_locked:
                return True
        elif is_cutting_node(node.parent):
            parent = node.parent
            children = parent.list_of_children()
            if len(children) == 2:
                left_size = children[0].bin.size[:2]
                right_size = children[1].bin.size[:2]
                if parent.direction == Direction.H:
                    if round(left_size[0], 4) < 0:
                        is_locked = True
                    size = (
                        round(left_size[0] + right_size[0], 4),
                        round(max(left_size[1], right_size[1]), 4)
                    )
                else:
                    if round(left_size[1], 4) < 0:
                        is_locked = True
                    size = (
                        round(max(left_size[0], right_size[0]), 4),
                        round(left_size[1] + right_size[1], 4)
                    )
            else:
                size = children[0].bin.size[:2]
            parent_bin = parent.parent.bin
            if size[0] > round(parent_bin.size[0], 4) or size[1] > round(parent_bin.size[1], 4):
                is_locked = True
            if is_locked:
                return True
    return False
