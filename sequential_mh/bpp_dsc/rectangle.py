from abc import ABC, abstractmethod
from copy import deepcopy
from enum import Enum
from dataclasses import dataclass
from operator import attrgetter, itemgetter
from itertools import groupby, product, chain
from typing import Optional, Union, Type

from .support import is_subrectangle, deformation
from .exception import DirectionError, SizeError, MaterialError
from .base_rect import Point, RectangleXY

from sequential_mh.tsh.rect import PackedRectangle


Number = Union[int, float]
Vec2 = tuple[Number, Number]


class BinType(Enum):
    """Класс типов контейнеров"""
    ingot = 'Слиток'  # исходный элемент
    leaf = 'Лист'
    adjacent = 'Смежный остаток'
    semifinished = 'Полуфабрикат'
    waste = 'Отходы'
    residue = 'Остаток'
    # unsizedbin = 'Лист с неопр. размерами'


class Rectangle3d:
    """Базовый класс параллелепипеда"""
    def __init__(self, length: Number,
                 width: Number, height: Number) -> Optional[Type[Exception]]:
        if length < 0 or width < 0 or height < 0:
            msg = f'Заданы некорректные размеры ({length}, {width}, {height})'
            raise SizeError(msg)
        self.length = length
        self.width = width
        self.height = height

    def is_subrectangle(self, rect, with_rotate=True) -> bool:
        """Возможность вписать прямоугольник в текущий

        :param rect: новый прямоугольник, который нужно вписать
        :type rect: Rectangle3d
        :param with_rotate: возможность вращения, по умолчанию True
        :type with_rotate: bool, optional
        :return: True, если новый прямоугольник можно вписать,
                 False в противном случае
        :rtype: bool
        """
        return is_subrectangle(rect.size, self.size, with_rotate=with_rotate)

    @property
    def area(self) -> Number:
        """Площадь большей (верхней) стороны

        :return: площадь
        :rtype: int или float
        """
        return self.length * self.width

    @property
    def volume(self) -> Number:
        """Объем

        :return: объем
        :rtype: int или float
        """
        return self.length * self.width * self.height

    @property
    def size(self) -> tuple[Number, Number, Number]:
        """Размеры прямоугольника

        :return: размеры в формате (длина, ширина, высота)
        :rtype: tuple[Number, Number, Number]
        """
        return self.length, self.width, self.height

    def eq_rot(self, obj) -> bool:
        """Сравнение с возможностью вращения

        :param obj: новый прямоугольник
        :type obj: Rectangle3d
        :return: результат сравнения
        :rtype: bool
        """
        condition_b = self.length == obj.width and self.width == obj.length
        condition_a = self.length == obj.length and self.width == obj.width
        return (condition_a or condition_b) and self.height == obj.height

    def __eq__(self, o) -> bool:
        condition_a = self.length == o.length and self.width == o.width
        return condition_a and self.height == o.height

    def __repr__(self):
        return (
            f'{self.__class__.__name__}'
            f'({self.length}, {self.width}, {self.height})'
        )


@dataclass
class Material:
    """Класс материала

    :ivar name: наименование материала
    :vartype name: str
    :ivar density: плотность материала
    :vartype density: int или float
    :ivar extension: коэффициент растяжения
    :vartype extension: int или float
    """
    name: str
    density: Number
    extension: Number


class BaseBin(Rectangle3d):
    """Базовый класс листа

    :ivar length: длина
    :vartype length: int или float
    :ivar width: ширина
    :vartype width: int или float
    :ivar height: толщина
    :vartype height: int или float
    :ivar material: материал
    :vartype material: Material или None, optional
    """
    def __init__(self, length: Number, width: Number, height: Number,
                 material: Optional[Material]=None) -> None:
        super().__init__(length, width, height)
        self.name = ''
        self.material = material

    @property
    def mass(self) -> Number:
        """Масса

        Если материал не указан, масса равна 0.

        :return: масса
        :rtype: int или float
        """
        if self.material:
            return self.volume * self.material.density
        return 0.

    def eq_rot(self, obj):
        return (
            self.material == obj.material and super().eq_rot(obj)
            # (super().__eq__(obj) or super().eq_rot(obj))
        )

    def __eq__(self, o) -> bool:
        return self.material == o.material and super().__eq__(o)


class Direction(Enum):
    """Класс направлений"""
    V = 0, 'вертикальное'
    H = 1, 'горизонтальное'


class Bin(BaseBin):
    """Класс листа-контейнера

    Предназначен для размещения на нем заготовок.

    :param length: длина
    :type length: int или float
    :param width: ширина
    :type width: int или float
    :param height: толщина
    :type height: int или float
    :param rolldir: направление проката
    :type rolldir: Direction или None, optional
    :param material: материал
    :type material: Material или None, optional
    :param bin_type: тип контейнера
    :type bin_type: BinType или None, optional

    :ivar length: длина
    :vartype length: int или float
    :ivar width: ширина
    :vartype width: int или float
    :ivar height: толщина
    :vartype height: int или float
    :ivar last_rolldir: направление последнего проката
    :vartype last_rolldir: Direction или None
    :ivar material: материал
    :vartype material: Material или None
    :ivar bin_type: тип контейнера, если соответствующий параметр не
                    передан, устанавливается как BinType.ingot
    :vartype bin_type: BinType
    """
    def __init__(self, length: Number, width: Number, height: Number,
                 rolldir: Optional[Direction]=None,
                 material: Optional[Material]=None,
                 bin_type: Optional[BinType]=None) -> None:
        super().__init__(length, width, height, material)
        self.last_rolldir = rolldir
        self.bin_type = bin_type or BinType.ingot

    def is_suitable(self, blank, with_def=False) -> Union[bool, Type[Exception]]:
        """Проверка заготовки на возможность размещения в контейнере

        Если заготовка должна располагаться по направлению проката,
        она будет развернута так, чтобы направление проката листа и
        заготовки совпадали.

        :param blank: экземпляр заготовки
        :type blank: Blank
        :raises DirectionError: если в контейнере не указано направление
                                проката, а заготовке вращение запрещено,
                                будет возбуждено исключение.
        :return: True, если размещение возможно, иначе False
        :rtype: Union[bool, Type[Exception]]
        """
        if not with_def or self.height == blank.height:
            if blank.is_rotatable:
                return super().is_subrectangle(blank, with_rotate=True)
            if self.last_rolldir:
                if self.last_rolldir != blank.direction:
                    blank.rotate()
                return super().is_subrectangle(blank, with_rotate=False)
            msg = f'Узел {self} не имеет направления проката'
            raise DirectionError(msg)
        if self.height > blank.height:
            flag = False
            flag += self._is_suitable_with_def(blank, Direction.H)
            flag += self._is_suitable_with_def(blank, Direction.V)
            return bool(flag)
        return False

    def _is_suitable_with_def(self, blank, rolldir):
        deformation_size = self.deformation(blank.height, rolldir)
        with_rotate = blank.is_rotatable
        if blank.direction != rolldir:
            blank.rotate()
        return is_subrectangle(
            blank.size, deformation_size, with_rotate=with_rotate
        )

    def deformation(self, new_height, rolldir):
        if self.material is None:
            raise MaterialError(f'У листа {self} не указан материал')
        length, width, height = self.size
        if rolldir == Direction.H:
            width = deformation(
                width, height, new_height, self.material.extension
            )
        else:
            length = deformation(
                length, height, new_height, self.material.extension
            )
        return length, width, new_height

    @property
    def rolldir(self) -> Optional[Direction]:
        """Направление последнего проката"""
        return self.last_rolldir


class Estimator:
    def __init__(self, bin: 'UnsizedBin', start=None, limits=None):
        self.bin = bin
        self.rectangle = RectangleXY((0, 0), (bin.width, bin.length))
        self.height = bin.height
        self.d_height = bin.d_height
        if start is None:
            start = self.rectangle.blp
        self.start = start
        self.limits = limits
        # self.parent = parent

    def update(self, rectangle, deformations):
        x, y = rectangle.trp
        dist = self(x, y, deformations)
        if dist is None:
            raise ValueError(f'Точка {(x, y)} лежит вне области')
        volume = self.rectangle.length * self.rectangle.width * self.height
        new_height = volume / (rectangle.length * rectangle.width)
        self.rectangle = rectangle
        self.height = new_height

    def cut(self, deformations, point=None):
        if point is None:
            x, y = self.tlp[0], self.trp[1]
        else:
            x, y = point
        dist = self(x, y, deformations)
        if dist is None:
            raise ValueError(f'Точка {(x, y)} лежит вне области')
        w_max, l_max = dist
        args = self.bin, self.d_height
        if w_max == 0 and l_max == 0:
            return []
        elif w_max == 0:
            return [self.__class__(*args, start=Point(self.start[0], y))]
        elif l_max == 0:
            return [self.__class__(*args, start=Point(x, self.start[1]))]
        else:
            # вертикальный разрез
            est1 = self.__class__(
                *args, start=Point(self.start[0], y), limits=(self.tlp[0], 0)
            )
            est2 = self.__class__(*args, start=Point(x, self.start[1]))
            # горизонтальный разрез
            est3 = self.__class__(*args, start=Point(self.start[0], y))
            est4 = self.__class__(
                *args, start=Point(x, self.start[1]), limits=(0, self.trp[1])
            )
            return [est1, est2, est3, est4]

    def estimate_max_size(self, x, y, deformations):
        x1, y1 = self.tlp
        x2, y2 = self.trp
        width = length = None
        if len(deformations) == 1:
            if deformations[0] == Direction.V:
                if x > x1 or y > y1:
                    raise ValueError(f'Точка {(x, y)} лежит вне области')
                return x1 - x, y1 - y
            else:
                if x > x2 and y > y2:
                    raise ValueError(f'Точка {(x, y)} лежит вне области')
                return x2 - x, y2 - y
        elif len(deformations) == 2:
            if x == 0 and y == 0:
                return x2, y1
            max_x = y2 * x1 * self.height / (self.d_height * y)
            max_y = y2 * x1 * self.height / (self.d_height * x)
            if x <= x1 and y <= y2:
                width, length = x2 - x, y1 - y
            elif x <= x1 and y2 < y <= y1:
                width, length = max_x - x, y1 - y
            elif x1 < x <= x2 and y <= y2:
                width, length = x2 - x, max_y - y
            elif x1 != x2 and y1 != y2 and x1 < x < x2 and y2 < y < y1 and y <= max_y:
                width, length = max_x - x, max_y - y

            if width is None and length is None:
                return None
            if self.limits and width and length:
                w_max, l_max = self.limits
                if w_max:
                    width = w_max if width > w_max else width
                else:
                    length = l_max if length > l_max else length
            return width, length
        else:
            raise ValueError('Некорректный список деформаций')

    @property
    def tlp(self):
        if self.limits:
            _, l_max = self.limits
            if l_max != 0:
                return self.trp

        x, y = self.rectangle.trp
        currency_h = self.height
        for h, group in groupby(self.bin.deformations, key=itemgetter(0)):
            group = [item for _, item in group]
            if Direction.V in group:
                y *= currency_h / h
            else:
                x *= currency_h / h
            currency_h = h
        return Point(x, y)
        # if len(self.bin.deformations) == 1:
        #     deform = self.bin.deformations[0]
        #     if deform == Direction.H:
        #         x = self.parent.tlp.x * self.parent.d_height / self.d_height
        #         y = self.parent.tlp.y
        #     else:
        #         x = self.parent.tlp.x
        #         y = self.parent.tlp.y * self.parent.d_height / self.d_height
        # else:
        #     x = self.parent.tlp.x
        #     y = self.parent.tlp.y * self.parent.d_height / self.d_height

    @property
    def trp(self):
        if self.limits:
            w_max, _ = self.limits
            if w_max != 0:
                return self.tlp

        x, y = self.rectangle.trp
        currency_h = self.height
        for h, group in groupby(self.bin.deformations, key=itemgetter(0)):
            group = [item for _, item in group]
            if Direction.H in group:
                x *= currency_h / h
            else:
                y *= currency_h / h
            currency_h = h
        return Point(x, y)

        # if self.parent is None or not self.bin.deformations:
        #     x, y = self.rectangle.blp
        #     return Point(self.max_width + x, self.rectangle.length + y)
        # if len(self.bin.deformations) == 1:
        #     deform = self.bin.deformations[0]
        #     if deform == Direction.H:
        #         x = self.parent.trp.x * self.parent.d_height / self.d_height
        #         y = self.parent.trp.y
        #     else:
        #         x = self.parent.trp.x
        #         y = self.parent.trp.y * self.parent.d_height / self.d_height
        # else:
        #     x = self.parent.trp.x * self.parent.d_height / self.d_height
        #     y = self.parent.trp.y

    @property
    def max_length(self):
        length = self.rectangle.length * self.height / self.d_height
        if self.limits:
            _, l_max = self.limits
            if l_max != 0:
                l_max -= self.rectangle.blp[1]
                return l_max if length > l_max else length
        return length

    @property
    def max_width(self):
        width = self.rectangle.width * self.height / self.d_height
        if self.limits:
            w_max, _ = self.limits
            if w_max != 0:
                w_max -= self.rectangle.blp[0]
                return w_max if width > w_max else width
        return width

    @property
    def min_length(self):
        return self.trp[1] - self.start[1]

    @property
    def min_width(self):
        return self.tlp[0] - self.start[0]

    def __call__(self, x, y, deformations):
        return self.estimate_max_size(x, y, deformations)

    def __repr__(self):
        return (
            f'{self.__class__.__name__}'
            f'({repr(self.bin)}, {self.d_height}, {self.parent})'
        )


class UnsizedBin(Bin):
    # TODO: доделать
    # сделать возможность указывать целевую толщину как None???
    def __init__(self, length: Number, width: Number, height: Number, d_height,
                 rolldir: Optional[Direction]=None,
                 material: Optional[Material]=None,
                 bin_type: Optional[BinType]=None) -> None:
        super().__init__(length, width, height, rolldir, material, bin_type)
        self.d_height = d_height
        # if rolldir:
        #     self.deformations = [rolldir]
        # else:
        self.deformations = []
        self.fixed_length = None
        self.fixed_width = None
        self.estimator = Estimator(self)

    def add_deformation(self, def_dir: tuple[float, Direction]):
        # if def_dir in self.deformations:
        #     msg = f'Деформация {def_dir} уже добавлена с список деформаций'
        #     raise ValueError(msg)
        # if len(self.deformations) == 2:
        #     msg = 'Превышено количество деформаций. Допустимо 2 деформации'
        #     raise ValueError(msg)
        # if self.last_rolldir is None:
        self.last_rolldir = def_dir[1]
        self.deformations.append(def_dir)

    def last_deformations(self):
        groups = {h: list(group) for h, group in groupby(self.deformations, key=itemgetter(0))}
        if self.d_height in groups:
            return groups[self.d_height]
        return []

    def fix_size(self, size):
        pass


class Blank(BaseBin):
    """Заготовка

    Предназначена для размещения в контейнере.

    :param length: длина
    :type length: int или float
    :param width: ширина
    :type width: int или float
    :param height: толщина
    :type height: int или float
    :param priority: приоритет (>= 1)
    :type priority: int
    :param direction: направление, если не указано или передано None.
    :type direction: Direction или None, optional
    :param material: материал
    :type material: Material или None, optional

    :ivar length: длина
    :vartype length: int или float
    :ivar width: ширина
    :vartype width: int или float
    :ivar height: толщина
    :vartype height: int или float
    :ivar priority: приоритет (>= 1), чем меньше значение, тем выше
                    приоритет, 1 - самый высокий приоритет.
    :vartype priority: int
    :ivar direction: Direction или None,
                     если None - направление размещения не важно.
    :vartype direction: Direction или None
    :ivar material: материал
    :vartype material: Material или None
    """
    def __init__(self, length: Number, width: Number, height: Number,
                 priority: int, direction: Optional[Direction]=None,
                 material: Optional[Material]=None) -> None:
        super().__init__(length, width, height, material=material)
        self.priority = priority
        self.direction = direction

    def rotate(self) -> None:
        """Вращение заготовки

        Если указано направление размещения, оно тоже будет изменено
        на противоположное.
        """
        self.length, self.width = self.width, self.length
        if self.direction is not None:
            if self.direction == Direction.H:
                self.direction = Direction.V
            else:
                self.direction = Direction.H

    @property
    def is_rotatable(self) -> bool:
        """Возможность свободного вращения"""
        return self.direction is None

    def __eq__(self, o) -> bool:
        if not isinstance(o, self.__class__):
            return False
        if self.direction and o.direction:
            if self.direction != o.direction:
                o.rotate()
                condition = super().__eq__(o)
                o.rotate()
            else:
                condition = super().__eq__(o)
        elif self.direction is None and o.direction is None:
            condition = super().eq_rot(o)
        else:
            condition = False
        return self.priority == o.priority and condition


# class PackedBlankProtocol(Protocol):
#     rectangle: RectangleXY
#     x: Number
#     y: Number

#     @property
#     def coordinates(self) -> Vec2:
#         """Координаты в виде кортежа"""
#         raise NotImplementedError


class PackedBlank(PackedRectangle):
    pass


# @dataclass
# class PackedBlank:
#     """Упакованная заготовка

#     :ivar blank: заготовка
#     :vartype blank: Blank
#     :ivar x: координата x
#     :vartype x: int или float
#     :ivar y: координата y
#     :vartype y: int или float
#     """
#     blank: Blank
#     x: Number
#     y: Number

#     @property
#     def coordinates(self) -> Vec2:
#         """Координаты в виде кортежа"""
#         return self.x, self.y


class ABCKit(ABC):
    """Абстрактный класс для набора заготовок"""
    @abstractmethod
    def qty_blank(self, blank):
        ...

    @property
    @abstractmethod
    def total_volume(self) -> Number:
        """Общий объем заготовок

        :return: объем заготовок
        :rtype: int или float
        """
        ...

    @property
    @abstractmethod
    def total_mass(self) -> Number:
        """Общая масса заготовок

        :return: масса заготовок
        :rtype: int или float
        """
        ...


PackedSubgroup = dict[Number, list[PackedBlank]]
Subgroup = dict[Number, list[Blank]]
Group = dict[Number, Subgroup]


class Kit(ABCKit):
    """Набор заготовок

    :param blanks: список заготовок
    :type blanks: Union[list[Blank], Group]

    :ivar blanks: заготовки, сгруппированные по толщине и приоритету
    :vartype blanks: Group
    """
    def __init__(self, blanks: Union[list[Blank], Group]) -> None:
        super().__init__()
        self.blanks = {}
        if isinstance(blanks, list):
            for height, group in groupby_blanks(blanks, attr='height').items():
                self.blanks[height] = groupby_blanks(group, attr='priority')
        else:
            self.blanks = blanks

    def sort(self, sorting: str='width'):
        """Сортировка заготовок

        Сортировку можно проводить либо по длине, либо по ширине.
        Для сортировки по длине необходимо задать параметр sorting
        равный 'length'. Сортировка производится по невозрастанию.

        :param sorting: параметр сортировки, по умолчанию 'width'
                        (сортировка по ширине). Сортировка по длине
                        задается значением 'length'.
        :type sorting: str, optional
        :raises ValueError: исключение возбуждается при передаче
                            значения параметра sorting отличного от
                            'width' или 'length'
        """
        if sorting not in ('width', 'length'):
            raise ValueError('The algorithm only supports sorting by width '
                             f'or length but {sorting} was given.')
        
        for _, group in self.blanks.items():
            rotate_all(group)
            for _, subgroup in group.items():
                for blank in subgroup:
                    if blank.length > blank.width:
                        blank.rotate()
                subgroup.sort(key=attrgetter(sorting), reverse=True)

    def unplaced(self, bin_item: Bin, height=None):
        all_blanks = []
        if height:
            if height <= bin_item.height:
                all_blanks.extend(
                    chain.from_iterable(self.blanks[height].values())
                )
        else:
            for height, group in self.blanks.items():
                if height <= bin_item.height:
                    all_blanks.extend(chain.from_iterable(group.values()))
        return all_blanks

    def available_blanks(self, bin_item: Bin, priority=None):
        if bin_item.height in self.blanks:
            if priority is None:
                all_blanks = chain.from_iterable(
                    self.blanks[bin_item.height].values()
                )
            else:
                all_blanks = self.blanks[bin_item.height][priority]
            return [o for o in all_blanks if bin_item.is_suitable(o)]
        return []

    def delete_items(self, items, height):
        if isinstance(items, list):
            items = sorted(items, key=attrgetter('priority'))
            items = {k: list(v) for k, v in groupby(items, key=attrgetter('priority'))}
        for key, values in items.items():
            if key in self.blanks[height]:
                for item in values:
                    self.blanks[height][key].remove(item)

    def separate(self, height: Number):
        blanks = deepcopy(self.blanks)
        new_kit = self.__class__({height: blanks.pop(height)})
        residual_kit = self.__class__(blanks)
        return new_kit, residual_kit

    def pop_height(self, height):
        if height in self:
            self.blanks.pop(height)

    def hp_sequence(self):
        sorted_height_priority = []
        for height, group in self.blanks.items():
            sorted_height_priority.extend(
                product((height, ), [p for p, v in group.items() if v])
            )
        sorted_height_priority = sorted(
            sorted_height_priority, key=lambda x: (x[1], -x[0])
        )
        return sorted_height_priority

    def hp_unplaced(self):
        return self.hp_sequence()[0]

    def update(self, blanks):
        if isinstance(blanks, list):
            blanks = groupby_blanks(blanks, attr='height')
            for height, group in blanks.items():
                blanks[height] = groupby_blanks(group, attr='priority')
        for height, group in blanks.items():
            if height in self.blanks:
                for priority, subgroup in group.items():
                    if priority in self.blanks[height]:
                        self.blanks[height][priority].extend(subgroup)
                    else:
                        self.blanks[height][priority] = subgroup
            else:
                self.blanks[height] = group

    def is_empty(self, height=None):
        if self.blanks:
            empty_flag = False
            if height is None:
                for _, group in self.blanks.items():
                    for _, subgroup in group.items():
                        empty_flag += bool(subgroup)
            else:
                if height in self.blanks:
                    for _, r_list in self.blanks[height].items():
                        empty_flag += bool(r_list)
            return not empty_flag
        return True

    def qty(self, height=None):  # кол-во заготовок
        qty = 0
        if height is None:
            for _, group in self.blanks.items():
                for _, subgroup in group.items():
                    qty += len(subgroup)
        else:
            for _, subgroup in self.blanks[height].items():
                qty += len(subgroup)
        return qty

    def qty_blank(self, blank):
        if blank.height in self.blanks and blank.priority in self.blanks[blank.height]:
            return sum(item.eq_rot(blank) for item in self.blanks[blank.height][blank.priority])
        return 0

    def delete_height(self, height):
        if height in self:
            self.blanks.pop(height)

    @property
    def max_height(self):
        return max(self.blanks.keys())

    @property
    def total_volume(self) -> Number:
        return sum(o.volume for o in self)

    @property
    def total_mass(self) -> Number:
        return sum(o.mass for o in self)
    
    def items(self):
        return self.blanks.items()

    def __getitem__(self, key):
        return self.blanks[key]

    def __contains__(self, key):
        return key in self.blanks

    def __iter__(self):
        for _, group in self.blanks.items():
            for _, subgroup in group.items():
                for item in subgroup:
                    yield item

    def __repr__(self):
        return f'{self.__class__.__name__}({list(self)})'


class Result(ABCKit):
    def __init__(self, blanks: PackedSubgroup, tailings, packing_len, packing_width,
                 height) -> None:
        super().__init__()
        self.blanks = blanks
        self.height = height
        self.length = packing_len
        self.width = packing_width
        self.tailings = tailings
        # self.hem = (0, 0)

    def update(self, blanks, tailings=None, hem=(0, 0)):
        if not blanks:
            return
        if isinstance(blanks, list):
            # key = 'blank.priority'
            key = 'rectangle.priority'
            blanks.sort(key=attrgetter(key))
            blanks = {
                k: list(v) for k, v in groupby(blanks, key=attrgetter(key))
            }
        for priority, group in blanks.items():
            if priority in self.blanks:
                self.blanks[priority].extend(group)
            else:
                self.blanks[priority] = group
        total_l, total_w = [], []
        for _, list_r in self.blanks.items():
            total_l.append(max([r.y + r.rectangle.length for r in list_r]))
            total_w.append(max([r.x + r.rectangle.width for r in list_r]))
        if tailings:
            total_l.append(max([r.y + r.length for r in tailings]))
            total_w.append(max([r.x + r.width for r in tailings]))
        self.length = max(total_l)  # + hem[1]
        self.width = max(total_w)   # + hem[0]
        self.tailings.extend(tailings)
        # self.hem = hem

    def qty(self):  # кол-во
        return sum(len(group) for _, group in self.blanks.items())

    def qty_blank(self, blank):
        if blank.height == self.height and blank.priority in self.blanks:
            return sum(
                # item.blank.eq_rot(blank) for item in self.blanks[blank.priority]
                item.rectangle.eq_rot(blank) for item in self.blanks[blank.priority]
            )
        return 0

    def is_packed(self, blank):
        if blank.height == self.height and blank.priority in self.blanks:
            for item in self.blanks[blank.priority]:
                # if item.blank == blank:
                if item.rectangle == blank:
                    return True
        return False

    @property
    def pure_length(self):
        return self.length  # - 2 * self.hem[1]

    @property
    def pure_width(self):
        return self.width  # - 2 * self.hem[0]

    @property
    def total_volume(self) -> Number:
        res = 0.
        for _, group in self.blanks.items():
            # res += sum(o.blank.volume for o in group)
            res += sum(o.rectangle.volume for o in group)
        return res

    @property
    def total_mass(self) -> Number:
        res = 0.
        for _, group in self.blanks.items():
            # res += sum(o.blank.mass for o in group)
            res += sum(o.rectangle.mass for o in group)
        return res

    @property
    def is_empty(self):
        return not (bool(self.length) and bool(self.width))

    def used_area(self):
        return self.width * self.length

    def efficiency(self) -> Number:
        if self.length == 0.:
            return 0.
        return self.total_volume / (self.width * self.length * self.height)

    def total_efficiency(self, length, width) -> Number:
        if self.length == 0. or length == 0 or width == 0:
            return 0.
        return self.total_volume / (width * length * self.height)

    def __iter__(self):
        return chain.from_iterable(self.blanks.values())


def groupby_blanks(blanks: list[Blank], *, attr) -> dict[int, list[Blank]]:
    blanks.sort(key=attrgetter(attr), reverse=True)
    return {
        k: list(group) for k, group in groupby(blanks, key=attrgetter(attr))
    }


def rotate_all(rectangles):
    for _, group in rectangles.items():
        for blank in group:
            if blank.length > blank.width and blank.is_rotatable:
                blank.rotate()
