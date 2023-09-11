import re

from lxml import etree


# 读取 SVG 文件

def get_x_node(node, min_x=100000000, max_x=-1):
    if node is None:
        return None, None

    if 'x' in node.attrib:
        x = int(node.attrib['x'])
        min_x = min(x, min_x)
        max_x = max(x, max_x)
    if 'd' in node.attrib:
        split = node.attrib['d'].split(" ")
        if "," in split[0]:
            for i in split:
                i_split = i.split(",")
                if i_split[0][0].isnumeric():
                    x = int(i_split[0])
                else:
                    x = int(i_split[0][1:])
                min_x = min(x, min_x)
                max_x = max(x, max_x)
        else:
            for i in range(0, len(split), 2):
                if split[i] == 'M':
                    continue
                x = int(split[i][1:])
                min_x = min(x, min_x)
                max_x = max(x, max_x)

    for child in node:
        child_min_x, child_max_x = get_x_node(child, min_x, max_x)
        if child_min_x:
            min_x = min(child_min_x, min_x)
        if child_max_x:
            max_x = max(child_max_x, max_x)

    return min_x, max_x


def get_y_node(node, min_y=100000000, max_y=-1):
    if node is None:
        return None, None

    if 'y' in node.attrib:
        y = int(node.attrib['y'])
        min_y = min(y, min_y)
        max_y = max(y, max_y)
    if 'd' in node.attrib:
        split = node.attrib['d'].split(" ")
        if "," in split[0]:
            for i in split:
                i_split = i.split(",")
                y = int(i_split[1])
                min_y = min(y, min_y)
                max_y = max(y, max_y)
        else:
            for i in range(1, len(split), 2):
                y = int(split[i])
                min_y = min(y, min_y)
                max_y = max(y, max_y)

    for child in node:
        child_min_x, child_max_x = get_y_node(child, min_y, max_y)
        if child_min_x and child_min_x < min_y:
            min_y = child_min_x
        if child_max_x and child_max_x > max_y:
            max_y = child_max_x

    return min_y, max_y


def get_default_y(y, x=3500, is_icon=False, icon_width=500):
    if y > 1000 and y < 3000:
        if is_icon:
            if x < 3500:
                return 1000 - icon_width - 300
            return 1000 - icon_width - 300
        return 1000
    if y > 3000 and y < 6000:
        if is_icon:
            return 4100 - icon_width
        return 4100
    if y > 6000:
        if is_icon:
            return 7100 - icon_width
        return 7100
    return y
    # raise ValueError("y is not in range:" + str(y))


def find_parent_with_class(node, target_class):
    while True:
        node = node.getparent()
        if node is None:
            return None
        if 'class' in node.attrib:
            if node.attrib['class'] == target_class:
                return node


def get_add_frame_svg(tree, node_id_list: list, path):
    if tree is None:
        tree = etree.parse(path)
    root = tree.getroot()

    for node_ids in node_id_list:
        node_id1 = node_ids[0]
        node_id2 = node_ids[1] if len(node_ids) > 1 else None
        if node_id1 is None and node_id2 is None:
            assert False
        node1 = get_node_by_id(node_id1, root)
        if len(node1) == 0:
            continue
        node2 = None
        if node_id2 is not None:
            node2 = get_node_by_id(node_id2, root)
        if node_id2 and not node2:
            print(f'Element with ID "{node_id2}" not found in the SVG.')
            assert False

        node1_min_x, node1_max_x = get_x_node(node1[0])
        staff_node1 = find_parent_with_class(node1[0], 'staff')
        if staff_node1 == None:
            staff_node1 = node1[0]
        node1_p_min_y, node1_p_max_y = get_y_node(staff_node1)

        width = node1_max_x - node1_min_x
        if node2:
            staff_node2 = find_parent_with_class(node2[0], 'staff')

            system_node1 = find_parent_with_class(node1[0], 'system')
            system_node2 = find_parent_with_class(node2[0], 'system')

            node2_min_x, node2_max_x = get_x_node(node2[0])
            node2_p_min_y, node2_p_max_y = get_y_node(staff_node2)
            width = node2_max_x - node1_min_x

            if system_node1 is not None and system_node2 is not None:
                if system_node1.attrib['id'] != system_node2.attrib['id']:
                    print("不在同一列")
                    x = node1_min_x - 80
                    y = node1_p_min_y - 80
                    height = node1_p_max_y - node1_p_min_y + 160
                    height = 1200 if height < 1000 else height
                    width = 19000 - x
                    rect = etree.Element('rect', id='box',
                                         x=str(x), y=str(y),
                                         width=str(width), height=str(height),
                                         stroke='red', fill='none')
                    rect.set("stroke-width", "80")
                    node1[0].getparent().append(rect)

                    x = 0
                    y = node2_p_min_y - 80
                    height = node2_p_max_y - node2_p_min_y + 160
                    height = 1200 if height < 1000 else height
                    width = node2_max_x + 160
                    rect = etree.Element('rect', id='box',
                                         x=str(x), y=str(y),
                                         width=str(width), height=str(height),
                                         stroke='red', fill='none')
                    rect.set("stroke-width", "80")
                    node1[0].getparent().append(rect)
                    return tree

        width = width + 160
        x = node1_min_x - 80
        y = node1_p_min_y - 80
        height = node1_p_max_y - node1_p_min_y + 160
        height = 1200 if height < 1000 else height
        # 创建一个矩形元素来表示框
        rect = etree.Element('rect', id='box',
                             x=str(x), y=str(y),
                             width=str(width), height=str(height),
                             stroke='red', fill='none')
        rect.set("stroke-width", "80")

        # 将矩形元素添加到根元素中
        node1[0].getparent().append(rect)
    return tree


def get_node_by_id(node_id: str, root):
    if node_id.startswith("."):
        match = re.match(r'\.(\w+)\[(\d+)\]', node_id)
        if match:
            class_name = match.group(1)  # 获取类名
            index = int(match.group(2))  # 获取索引
            return [root.xpath('//*[@class="%s"]' % class_name)[index]]
        else:
            exit(-2)

    nodes = root.xpath('//*[@id="%s"]' % node_id)
    return nodes


def get_add_icon_svg(tree, icon_list: list, path):
    if not tree:
        tree = etree.parse(path)
    root = tree.getroot()

    for icon in icon_list:
        image = icon['image']
        selector = icon['selector']
        node = get_node_by_id(selector, root)
        if len(node) == 0:
            continue

        parent_node = node[0].getparent()
        if parent_node is None:
            parent_node = node[0]
        if 'class' in parent_node.attrib:
            if parent_node.attrib['class'] == 'system':
                parent_node = node[0]

        node1_min_x, node1_max_x = get_x_node(node[0])
        node1_p_min_y, node1_p_max_y = get_y_node(parent_node)

        x = node1_min_x
        y = get_default_y(node1_p_min_y, node1_min_x, True)
        width = 500
        height = 500

        # 创建一个矩形元素来表示框
        rect = etree.Element('image', id='image',
                             x=str(x), y=str(y),
                             width=str(width), height=str(height))

        rect.set("{http://www.w3.org/1999/xlink}href", "../" + image)

        # 将矩形元素添加到根元素中
        node[0].getparent().append(rect)

    # 保存更新后的 SVG 文件
    return tree


def get_add_text_svg(tree, text_list: list, path):
    if not tree:
        tree = etree.parse(path)
    root = tree.getroot()

    for icon in text_list:
        text = icon['text']
        selector = icon['selector']
        node = get_node_by_id(selector, root)
        if len(node) == 0:
            continue

        parent_node = node[0].getparent()
        if parent_node is None:
            parent_node = node[0]
        if 'class' in parent_node.attrib:
            if parent_node.attrib['class'] == 'system':
                parent_node = node[0]

        node1_min_x, node1_max_x = get_x_node(node[0])
        node1_p_min_y, node1_p_max_y = get_y_node(parent_node)

        x = node1_min_x
        y = get_default_y(node1_p_min_y, node1_min_x, False)
        width = 500
        height = 500

        # 创建一个矩形元素来表示框
        rect = etree.Element('text', id='text',
                             x=str(x), y=str(y))
        rect.set("font-size", "500")
        rect.text = text

        rect.set("{http://www.w3.org/1999/xlink}href", "../" + text)

        # 将矩形元素添加到根元素中
        node[0].getparent().append(rect)

    # 保存更新后的 SVG 文件
    return tree

def get_svg_and_hide_node(tree, id_list: list, path):
    if not tree:
        tree = etree.parse(path)
    root = tree.getroot()

    for id in id_list:
        node = get_node_by_id(id, root)
        if len(node) == 0:
            continue

        node[0].set("visibility", "hidden")

    return tree



def sava_svg(tree, path):
    # 保存更新后的 SVG 文件
    svg_ = path[:-4] + "-new.svg"
    tree.write(svg_, pretty_print=True)


if __name__ == '__main__':
    path = "yangying/中级综合模拟测试（一）/score/"
    # 要创建框的元素的 ID
    target_id = [[".beam[3]", ".beam[4]"]]
    # target_id2 = 'note-0000001998559704'
    svg_path = "6249.svg"
    svg = None
    # svg = get_add_frame_svg(None, target_id, path + svg_path)
    # svg = get_add_icon_svg(svg,
    #                        [{"image": "image/982_2018_05_03_image_982_1525324663982_15X20.png",
    #                          "selector": "measure-0000000880472434"},
    #                         {"image": "image/982_2018_05_03_image_982_1525324663982_15X20.png",
    #                          "selector": "measure-0000000160028709"},
    #                         {"image": "image/982_2018_05_03_image_982_1525324663982_15X20.png",
    #                          "selector": "measure-0000001403156630"},
    #                         {"image": "image/982_2018_05_03_image_982_1525324663982_15X20.png",
    #                          "selector": "measure-0000000239985718"}],
    #                        path + svg_path)
    # svg = get_add_text_svg(svg,
    #                        [{"selector": "note-0000000415156637", "text": "①"},
    #                         {"selector": "note-0000002125363637", "text": "②"},
    #                         {"selector": "note-0000000237335382", "text": "③"},
    #                         {"selector": "note-0000000300899360", "text": "④"}],
    #                        path + svg_path)
    svg = get_svg_and_hide_node(svg, ["note-0000000415156637"], path + svg_path)
    sava_svg(svg, path + svg_path)
