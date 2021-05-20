from ..bpp_dsc.stm import stmh_idrd
# from sequential_mh.bpp_dsc.graph import plot, create_edges


def optimal_ingot_size(tree, min_size, max_size, restrictions):
    # max_length, max_width, max_height = max_size
    min_length, min_width, min_height = min_size

    tree = stmh_idrd(tree, with_filter=False, restrictions=restrictions)

    # graph1, all_nodes1 = plot(tree.root, 'pdf/graph0.gv')
    # create_edges(graph1, all_nodes1)
    # graph1.view()

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
    # graph1, all_nodes1 = plot(tree.root, 'pdf/graph3.gv')
    # create_edges(graph1, all_nodes1)
    # graph1.view()

    # TODO: Проблема в том, что тип разреза не обновляется
    # может случиться так, что резать нужно будет по другому! (в 7 примере)
    tree.root.update_size()

    return tree
