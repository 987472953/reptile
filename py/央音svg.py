import os.path
import re

import cairosvg
from lxml import etree
from PIL import Image
import io
import base64


# 读取 SVG 文件

def get_x_node(node, min_x=100000000, max_x=-1):
    if node is None:
        return None, None

    width = 0
    if 'width' in node.attrib:
        width = int(node.attrib['width'].replace("px", ""))

    if 'x' in node.attrib:
        x = int(node.attrib['x'])
        min_x = min(x, min_x)
        max_x = max(x + width, max_x)
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
                max_x = max(x + width, max_x)
        else:
            for i in range(0, len(split), 2):
                if split[i] == 'M':
                    continue
                x = int(split[i][1:])
                min_x = min(x, min_x)
                max_x = max(x + width, max_x)

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

    height = 0
    # if 'height' in node.attrib:
    #     height = int(node.attrib['height'].replace("px", ""))

    if 'y' in node.attrib:
        y = int(node.attrib['y'])
        min_y = min(y, min_y)
        max_y = max(y + height, max_y)
    if 'd' in node.attrib:
        split = node.attrib['d'].split(" ")
        if "," in split[0]:
            for i in split:
                i_split = i.split(",")
                y = int(i_split[1])
                min_y = min(y, min_y)
                max_y = max(y + height, max_y)
        else:
            for i in range(1, len(split), 2):
                y = int(split[i])
                min_y = min(y, min_y)
                max_y = max(y + height, max_y)

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
        staff_node1 = find_parent_with_class(node1[0], 'system')
        if staff_node1 == None:
            staff_node1 = node1[0]
        node1_p_min_y, node1_p_max_y = get_y_node(staff_node1)

        width = node1_max_x - node1_min_x
        if node2:
            staff_node2 = find_parent_with_class(node2[0], 'system')

            system_node1 = find_parent_with_class(node1[0], 'system')
            system_node2 = find_parent_with_class(node2[0], 'system')

            node2_min_x, node2_max_x = get_x_node(node2[0])
            node2_p_min_y, node2_p_max_y = get_y_node(staff_node2)
            width = node2_max_x - node1_min_x

            if system_node1 is not None and system_node2 is not None:
                if system_node1.attrib['id'] != system_node2.attrib['id']:
                    print("不在同一列")
                    x = node1_min_x - 80
                    y = node1_p_min_y
                    height = node1_p_max_y - node1_p_min_y
                    height = 1200 if height < 1000 else height
                    width = 19000 - x
                    rect = etree.Element('rect', id='box',
                                         x=str(x), y=str(y),
                                         width=str(width), height=str(height),
                                         stroke='red', fill='none')
                    rect.set("stroke-width", "80")
                    node1[0].getparent().append(rect)

                    x = 0
                    y = node2_p_min_y
                    height = node2_p_max_y - node2_p_min_y
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
        x = node1_min_x - 160
        y = node1_p_min_y
        height = node1_p_max_y - node1_p_min_y
        height = 1200 if height < 1200 else height
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


def get_node_by_class(node_class: str, root):
    return root.xpath('//*[@class="%s"]' % node_class)


def get_add_icon_svg(tree, icon_list: list, path):
    if not tree:
        tree = etree.parse(path)
    root = tree.getroot()

    for icon in icon_list:
        image = icon['image']
        format = image[-3:]
        image = Image.open(os.path.join("yangying/中级综合模拟测试（一）", image))
        # 编码位图图像为Base64字符串
        image_buffer = io.BytesIO()
        image.save(image_buffer, format=format)
        base64_image = base64.b64encode(image_buffer.getvalue()).decode()

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

        rect.set("{http://www.w3.org/1999/xlink}href", f"data:image/{format};base64,{base64_image}")

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


def sava_svg(tree, path, new_path=None):
    if not tree:
        tree = etree.parse(path)

    # 保存更新后的 SVG 文件
    nodes_class = get_node_by_class("definition-scale", tree)

    if len(nodes_class) > 1:
        print("nodes_class len != 1" + path)
        exit(-1)
    if len(nodes_class) == 1:
        box_ = nodes_class[0].attrib['viewBox']
        getparent = nodes_class[0].getparent()
        getparent.set("viewBox", box_)
        getparent.append(*nodes_class[0].getchildren())
        getparent.remove(nodes_class[0])

    if new_path == None:
        svg_ = path[:-3] + "svg"
    else:
        svg_ = new_path
    tree.write(svg_, pretty_print=True, encoding="UTF-8", xml_declaration=True)


if __name__ == '__main__':
    path = "yangying/初级综合模拟测试（一）/score1/"
    # 要创建框的元素的 ID
    target_id = [["note-0000001285762267", "note-0000002073445200"]]
    # target_id2 = 'note-0000001998559704'
    svg_path = "6213.svg"
    svg = None
    svg = get_add_frame_svg(None, target_id, path + svg_path)
    # svg = get_add_icon_svg(svg,
    #                        [{"image": "image/982_2018_05_03_image_982_1525324663982_15X20.png",
    #                          "selector": "note-0000002005620308"},
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
    # svg = get_svg_and_hide_node(svg, ["note-0000000415156637"], path + svg_path)
    sava_svg(svg, path + svg_path)
    with open(path + svg_path, "rb") as svg_file:
        svg_data = svg_file.read()
        cairosvg.svg2png(bytestring=svg_data, write_to="output.png")
