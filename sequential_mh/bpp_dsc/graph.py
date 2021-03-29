"""Модуль визуализации дерева раскроя

:Date: 20.08.2020
:Version: 0.1
:Authors:
    - Воронов Владимир Сергеевич
"""

import graphviz

from .rectangle import BinType, UnsizedBin
from .tree import (
    BinNode, CuttingChartNode, Operations, is_op_node
)


def plot(root, filename):
    """Построение дерева схемы раскроя

    :param root: Корень дерева
    :type root: BinNode
    :param filename: имя файла
    :type filename: str
    :return: граф и набор нод в виде словаря, где ключи - id ноды,
             а значения - объекты
    :rtype: tuple[graphviz.dot.Digraph, dict[str, Node]]
    """
    graph = graphviz.Digraph(filename=filename)
    level = [root]
    all_nodes = {}
    new_level = []
    while level:
        with graph.subgraph() as subgraph:
            subgraph.attr(rank='same')
            node = level.pop(0)
            new_level.extend(node.list_of_children())
            name = create_name(node)
            color = 'lightblue'
            if node.locked:
                color = 'gray'
            elif isinstance(node, BinNode):
                if node.bin.bin_type in (BinType.ingot, BinType.adjacent):
                    color = 'orange'
                else:
                    color = 'forestgreen'
            elif isinstance(node, CuttingChartNode):
                color = 'firebrick1'
            subgraph.node(str(id(node)), name, style='filled', color=color)
            all_nodes[str(id(node))] = node
        if not level:
            level = new_level
            new_level = []
    return graph, all_nodes


def create_edges(graph, all_nodes):
    """Создание связей в дереве

    :param graph: граф
    :type graph: graphviz.dot.Digraph
    :param all_nodes: список узлов
    :type all_nodes: dict[str, Node]
    """
    for name, node in all_nodes.items():
        for chield in node.list_of_children():
            key = [k for k in all_nodes.keys() if str(id(chield)) == k]
            graph.edge(name, key[0])


def create_name(node, kit=False) -> str:
    """Создание подписи ноды

    :param node: узел дерева
    :type node: Node
    :param kit: флаг указания набора заготовок, defaults to False
    :type kit: bool, optional
    :return: имя узла
    :rtype: str
    """
    name = f'{node.__class__.__name__}\n'
    if isinstance(node, BinNode):
        if isinstance(node.bin, UnsizedBin):
            name += 'UnsizedBin\n'
        name += (
            f'{node.bin.length:.1f}x{node.bin.width:.1f}x{node.bin.height:.1f}'
            f'\n{node.bin.bin_type.value}\n'
        )
        if isinstance(node.bin, UnsizedBin):
            name += f'{node.bin.deformations}\n{node.bin.d_height}'
        if kit:
            name += f'{node.kit}'
    elif isinstance(node, CuttingChartNode):
        efficiency = node.result.total_efficiency(
            node.bin.length, node.bin.width
        )
        name += f'Схема раскроя {efficiency:.4f}\n'
        name += f'{node.result.pure_length:.1f}, {node.result.pure_width:.1f}'
    elif is_op_node(node) and node.operation == Operations.cutting:
        if node.direction:
            name += f'{node.operation.value}\n{node.direction.value}'
        else:
            print('---->')
            name += 'без разреза'
    else:
        name += f'{node.operation.value}'
    return name + f'\n{node._id}'
