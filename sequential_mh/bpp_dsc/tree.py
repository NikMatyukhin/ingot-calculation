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
from itertools import chain, product


from .ph import ph_bpp
from .support import deformation, is_subrectangle, is_subrectangle_with_def
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


cur_id = 0  # FIXME: удалить


class Operations(Enum):
    """Класс типов операций"""
    rolling = 'Прокат'
    v_rolling = 'Вертикальный прокат'
    h_rolling = 'Горизонтальный прокат'
    cutting = 'Разрез'
    packing = 'Упаковка'


class BaseNode:
    def __init__(self, children=None, parent=None) -> None:
        self.parent = parent
        self._children = children

        self._id = cur_id  # TODO: удалить
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
            rolling_node.delete(cur_branch)
            return rolling_node
        # if rolling_node.children is None:
        #     cur_branch = rolling_node.current_branch()
        #     cur_branch.parent.delete(cur_branch)

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
        src = node = self
        while node:
            children = node.list_of_children()
            if len(children) != 2:
                if is_ingot_node(node.parent):
                    return node
                src = node
                node = node.parent
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
                # return [item for item in children if item is src][0]
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
            
            global cur_id  # TODO: УДАЛИТЬ
            if isinstance(node, tuple):
                for i in node:
                    cur_id += 1
                    i._id = cur_id
            else:
                cur_id += 1
                node._id = cur_id

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
        print(cut_thickness, height)
        if not cut_thickness or (cut_thickness and height <= cut_thickness):
            left = OperationNode(Operations.cutting)
            right = OperationNode(Operations.rolling)
            return left, right

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
        # print(self, self.parent, self.children)
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
        print('--> = ', self)
        node = self
        parent = node.parent
        if node.is_troot():
            return False
        while parent.parent is not None and not parent.is_troot():
            node = parent
            parent = node.parent
            # if hasattr(parent, 'bin'):
            #     print('->', node, parent, parent.bin.bin_type)
            # else:
            #     print('->', node, parent)
        return node is parent.list_of_children()[1]

    def fix_sizes(self, width, length, is_min=False, miss_bins=False,
                  max_len=None, max_size=None, restrictions=None):
        # Лучше разнести этот метод по разным классам
        p_cont = self.parent_cont
        if miss_bins:
            if not is_ubin_node(self):
                p_cont.fix_sizes(
                    self.bin.width, self.bin.length, is_min=is_min,
                    miss_bins=miss_bins, max_size=max_size,
                    restrictions=restrictions
                )
                return
        else:
            if not is_ubin_node(self):
                return
        troot = self.get_troot()
        if is_ubin_node(troot) and troot.bin.bin_type == BinType.INTERMEDIATE:
            print('Правая ветка')
            pass
        elif is_ubin_node(troot) and self.in_right_branch():
            return
        if width == 0 or length == 0:
            return
        last_deformations = [item for _, item in self.bin.last_deformations()]
        last_rolldir = last_deformations[-1]
        # если потомок упаковка (то фиксируем без всего)
        if self.children and is_packing_node(self.children):
            print('Фиксация бина полуфабриката')
            if is_cutting_node(self.parent):
                estimate = self.parent.children[0].estimate_size()
            else:
                estimate = (0, 0)
            if last_deformations[-1] == Direction.H:
                length = max(length, p_cont.bin.length, estimate[LENGTH])
                if max_size and (length > max_size[WIDTH] or width > max_size[LENGTH]):
                    self.locked = True
                    if not is_cutting_node(self.parent):
                        node = self.delete_branch()
                        return
            else:
                width = max(width, p_cont.bin.width, estimate[WIDTH])
                if max_size and (width > max_size[WIDTH] or length > max_size[LENGTH]):
                    self.locked = True
                    if not is_cutting_node(self.parent):
                        node = self.delete_branch()
                        return
            bin_ = Bin(
                length, width, self.bin.d_height,
                self.bin.last_rolldir, self.bin.material, self.bin.bin_type
            )
            self.bin = bin_
            parent = self.get_parent_ubin()
            parent.fix_sizes(
                width, length, is_min=is_min, max_size=max_size,
                restrictions=restrictions
            )
        elif len(last_deformations) == 2:
            print('Фиксация бина с двумя деформациями')
            if is_cutting_node(self.parent):
                neighbour = [is_bin_node(node.children) for node in self.children.children]
                if not all(neighbour):
                    return
                estimate = self.estimate_size()
                width = estimate[WIDTH]
                length = estimate[LENGTH]
                dist = self.bin.estimator(width, length, last_deformations)
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
                    if max_size and (length > max_size[WIDTH] or width > max_size[LENGTH]):
                        self.locked = True
                        node = self.delete_branch()
                        if is_op_node(node):
                            neighbour = node.parent.nearest_descendant_bins()
                        else:
                            neighbour = node.nearest_descendant_bins()
                        neighbour = [is_bin_node(node) for node in neighbour]
                        if all(neighbour):
                            node.parent.fix_sizes(
                                width, length, is_min=is_min,
                                max_size=max_size, restrictions=restrictions
                            )
                        return
                else:
                    length += dist[1]
                    if max_size and (width > max_size[WIDTH] or length > max_size[LENGTH]):
                        self.locked = True
                        node = self.delete_branch()
                        if is_op_node(node):
                            pp = node.parent
                            neighbour = node.parent.nearest_descendant_bins()
                        else:
                            pp = node
                            neighbour = node.nearest_descendant_bins()
                        neighbour = [is_bin_node(node) for node in neighbour]
                        if all(neighbour):
                            pp.fix_sizes(
                                width, length, is_min=is_min,
                                max_size=max_size, restrictions=restrictions
                            )
                        return
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
            print('Фиксация бина с одной деф')
            last_rolldir = last_deformations[-1]
            if p_cont is not troot and is_ubin_node(p_cont):
                current_height = (p_cont.bin.d_height - self.bin.d_height) / 2 + self.bin.d_height
                if last_rolldir == Direction.H:
                    if max_size:
                        new_length = max_size[WIDTH]
                        if length >= new_length:
                            current_height = length * self.bin.d_height / new_length
                            if current_height > p_cont.bin.d_height:
                                current_height = p_cont.bin.d_height
                    length = length * self.bin.d_height / current_height
                else:
                    if max_size:
                        new_width = max_size[WIDTH]
                        if width >= new_width:
                            current_height = width * self.bin.d_height / new_width
                            if current_height > p_cont.bin.d_height:
                                current_height = p_cont.bin.d_height
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
            elif is_ubin_node(troot):
                if troot.bin.bin_type == BinType.INTERMEDIATE:
                    if last_rolldir == Direction.H:
                        if max_size:
                            new_length = max_size[WIDTH]
                            if length >= new_length:
                                current_height = length * self.bin.d_height / new_length
                                if current_height > p_cont.bin.d_height:
                                    current_height = p_cont.bin.d_height
                        else:
                            current_height = (p_cont.bin.d_height - self.bin.d_height) / 2 + self.bin.d_height
                        length = length * self.bin.d_height / current_height
                    else:
                        if max_size:
                            new_width = max_size[WIDTH]
                            if width >= new_width:
                                current_height = width * self.bin.d_height / new_width
                                if current_height > p_cont.bin.d_height:
                                    current_height = p_cont.bin.d_height
                        else:
                            current_height = (p_cont.bin.d_height - self.bin.d_height) / 2 + self.bin.d_height
                        width = width * self.bin.d_height / current_height
                    bin_ = Bin(
                        length, width, current_height,
                        last_rolldir, self.bin.material, self.bin.bin_type
                    )
                    self.bin = bin_
                    neighbour = self.get_bin_neighbors(troot)
                    neighbour = [is_bin_node(node) for node in neighbour]
                    if all(neighbour):
                        troot.fix_sizes(
                            width, length, is_min=is_min, max_size=max_size,
                            restrictions=restrictions
                        )
                return
            if not is_ubin_node(p_cont) or self.in_right_branch():
                if p_cont.bin.bin_type == BinType.leaf:
                    # устанавливаем минимальные размеры (у себя и у предка!!!)
                    if last_rolldir == Direction.H:
                        current_height = length * self.bin.d_height / p_cont.bin.length
                        length = p_cont.bin.length
                        # FIXME: доделать удаление веток
                        if max_size and length > max_size[WIDTH]:
                            self.locked = True
                    else:
                        current_height = width * self.bin.d_height / p_cont.bin.width
                        width = p_cont.bin.width
                else:
                    if last_rolldir == Direction.H:
                        length = p_cont.bin.length
                        current_height = p_cont.bin.width * p_cont.bin.height / width
                    else:
                        width = p_cont.bin.width
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
            # print('Бин без деформаций (ветка разреза)')
            height = p_cont.bin.height
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
            self.update_size(max_len=max_len)

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

        global cur_id  # FIXME: УДАЛИТЬ
        if isinstance(node, tuple):
            for i in node:
                cur_id += 1
                i._id = cur_id
        else:
            cur_id += 1
            node._id = cur_id

        return node

    def _create_nodes_rolling(self, rolled_height, double_sided=True, **kwargs):
        """Создание потомков при прокате"""
        if self.operation == Operations.rolling:
            # pparent = self.parent.parent
            # if is_adj_node(self.parent):
            vertical = OperationNode(Operations.v_rolling)
            horizontal = OperationNode(Operations.h_rolling)
            return vertical, horizontal
            # return OperationNode(Operations.v_rolling)
            # if is_op_node(pparent) and pparent.operation == Operations.cutting:
            #     return OperationNode(Operations.v_rolling)
            # создание двух узлов с разными направлениями
        # создание одного бина с модифицированными размерами
        parent_bn = self.parent_bnode
        # parent_bn = self.parent_cont
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

        # is_intermediate = 'cut_thickness' in kwargs
        cut_thickness = kwargs.get('cut_thickness')
        if is_ubin_node(self.parent_cont):
            height = self.parent_cont.bin.d_height
        else:
            height = parent_bn.bin.height
        print(f'{cut_thickness = }')
        is_intermediate = bool(cut_thickness) # and height == cut_thickness
        print(f'{cut_thickness = }')

        if is_intermediate and not is_op_node(self.parent):  #  and self.parent.operation != Operations.rolling
            # bin_type = BinType.adjacent
            bin_type = BinType.INTERMEDIATE

        if double_sided:
            parent_bn = self.parent_cont
            bin_ = UnsizedBin(
                *size, rolled_height,  # rolldir=rolldir
                material=parent_bn.bin.material, bin_type=bin_type
            )
            # print(bin_.deformations)
            if is_ubin_node(parent_bn):
                # previous_def = self.parent.bin.deformations[-1]
                for d in parent_bn.bin.deformations:
                    bin_.add_deformation(d)
            # print('--> ', bin_.deformations)
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
        # parent_bn = self.parent_bnode
        parent_bn = self.parent
        if parent_bn is None:
            raise ParentNodeError(f'Узел {self} не имеет предка')
        # bin_ = self.parent_bnode.bin
        # kit = self.parent_bnode.kit
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
        # return CuttingChartNode(self.parent_bnode.bin)
        # print(self.parent.bin)
        return CuttingChartNode(self.parent.bin)

    # работа с размерами (оценка, обновление) --------------------------
    def estimate_size(self, *, start=None):
        estimate = super().estimate_size(start=start)
        # parent_bin = self.parent_bnode.bin
        parent_bin = self.parent_cont.bin
        if is_ubin_node(self.parent_cont):
            height = parent_bin.d_height
        else:
            height = parent_bin.height
        if self.operation == Operations.cutting:
            if self.direction is None:
                print('Нет разреза', estimate)
                return (0, 0, height)
                # msg = f'Узел {self} не содержит направление разреза'
                # raise OperationNodeError(msg)
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
            print(estimate)
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
            else:
                right.bin.width = self.point[WIDTH]
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
            # childe_bin.height = parent_size[HEIGHT]
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
            # перенос всех размеров, без требований к разрезу
            # FIXME: можно ставить ода нуля когда разрез не указан
            # в остальных случаях нулем делать одну из сторон
            src.bin.length = 0.
            src.bin.width = 0.
            dst.bin.length = size[LENGTH]
            dst.bin.width = size[WIDTH]
        else:
            if is_ubin_node(self.children[0]):
                print(f'-------> {estimate = }')
                used_volume = estimate[0] * estimate[1] * estimate[2]
                free_volume = self.children[0].bin.volume - used_volume
                length, width = 50, 50
                height = free_volume / (length * width)
                print(f'Используемый объем: {used_volume}')
                print(f'Общий объем: {self.children[0].bin.volume}')
                print(f'Примерная толщина при размерах 50x50: {height}')
                # src.bin.length = estimate[LENGTH]
                dst.bin.length = length
                dst.bin.width = width
                dst.bin.height = height
                # TODO: Доделать перенос объема
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
                    if s_1 >= s_2:
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
                if s_1 >= s_2:
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
        # max_width, max_length = max_size[height > 3]
        # max_size = max_size[height > 3]
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
            # self.hem = (0, hem)
            self.y_hem = (hem, hem)
            if bin_node.parent.direction == Direction.H:
                self.x_hem = (end * length, 0)
            else:
                self.x_hem = (end * length, end * length)
        else:
            self.hem = (0, hem)
            self.x_hem = (hem, hem)
            if bin_node.parent.direction == Direction.H:
                self.y_hem = (end * width, 0)
            else:
                self.y_hem = (end * width, end * width)

        if isinstance(self.bin, UnsizedBin):
            group = bin_node.kit[self.bin.d_height]
            _, main_region, min_rect, result, unplaced, tailings = bpp_ts(
                bin_node.bin.length, bin_node.bin.width, bin_node.bin.height,
                bin_node.bin.d_height, group, x_hem=self.x_hem, y_hem=self.y_hem,
                allowance=allowance, max_size=max_size,
                is_visualize=False
            )
            # width, length = main_region.rectangle.trp
            width, length = min_rect.width, min_rect.length
            # width += self.hem[Direction.V.value[0]]
            # length += self.hem[Direction.H.value[0]]
            self.bin = Bin(
                length, width, bin_node.bin.d_height,
                self.bin.last_rolldir, self.bin.material, self.bin.bin_type
            )
            self.result.update(result, tailings=tailings)
            bin_node.fix_sizes(
                width, length, max_size=max_size, restrictions=restrictions
            )
        else:
            length, width, _ = self.available_size()
            # y_0 += hem[Direction.H.value]
            # length -= hem[Direction.H.value]
            # x_0 += hem[Direction.V.value]
            # width -= hem[Direction.V.value]
            group = bin_node.kit[self.bin.height]
            result, total_len, total_width, _ = ph_bpp(
                length, width, group, x0=x_0, y0=y_0, first_priority=True
            )
            self.result.update(result, tailings=None)

        if self.result.is_empty:
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
        estimate = self.estimate_size()
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
        # if self.parent_bnode:
        if self.parent.parent:
            return self.parent.parent.kit
            # msg = (
            #     f'Узел {self} должен иметь предка типа BinNode, '
            #     f'текущий предок {self.parent}'
            # )
            # raise ParentNodeError(msg)
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


def solution_efficiency(root, path, nd=False, is_total=False):
    print('-> Эффективность решения')
    # is_total - Учитывая весь бин
    # nd - взвешенная на количество деталей
    used_total_volume = 0.
    used_volume = 0.
    number_detail = 0
    for node in path:
        if is_cc_node(node):
            used_total_volume += node.bin.volume
            used_volume += node.result.total_volume
            number_detail += node.result.qty()
    if is_total:
        efficiency = used_volume / root.bin.volume
    else:
        if used_total_volume == 0:
            efficiency = 0
        else:
            efficiency = used_volume / used_total_volume
    print(f'Упаковано деталей: {number_detail}')
    if nd and number_detail:
        efficiency *= number_detail / root.kit.qty()
    return efficiency


def optimal_configuration(tree, lower=1., nd=False, is_total=False):
    print('-> Оптимальная конфигурация')
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
    #     result = [
    #         item for item in solutions
    #         if solution_efficiency(item[-1], item[:-1], True) >= lower
    #     ]
    # root = copy(tree.root)
    # nodes = []
    # level = deque([(root, tree.root)])
    # while level:
    #     dst, src = level.popleft()
    #     for childe in src.list_of_children():
    #         if childe in result:
    #             new_childe = copy(childe)
    #             dst.add(new_childe)
    #             nodes.append(new_childe)
    #             level.append((new_childe, childe))
    # return root, nodes


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
    return isinstance(node, BinNode) and not isinstance(node.bin, UnsizedBin)


def is_ubin_node(node) -> bool:
    return isinstance(node, BinNode) and isinstance(node.bin, UnsizedBin)


def is_ingot_node(node):
    return is_bin_node(node) and node.bin.bin_type == BinType.ingot


def is_op_node(node) -> bool:
    return isinstance(node, OperationNode)


def is_rolling_node(node):
    return is_op_node(node) and node.operation in (
        Operations.rolling, Operations.h_rolling, Operations.v_rolling
    )


def is_cutting_node(node):
    return is_op_node(node) and node.operation == Operations.cutting


def is_packing_node(node):
    return is_op_node(node) and node.operation == Operations.packing


def is_cc_node(node) -> bool:
    return isinstance(node, CuttingChartNode)


def is_adj_node(node) -> bool:
    return (
        (is_bin_node(node) or is_ubin_node(node)) and
        node.bin.bin_type in (BinType.adjacent, BinType.ingot,
                              BinType.INTERMEDIATE)
    )


def is_imt_node(node):
    return (
        (is_bin_node(node) or is_ubin_node(node)) and
        node.bin.bin_type == BinType.INTERMEDIATE
    )
