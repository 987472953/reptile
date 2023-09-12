import json
import os
import shutil
import traceback
import zipfile

from py.央音svg import get_add_frame_svg, get_add_icon_svg, sava_svg, get_add_text_svg, get_svg_and_hide_node

# 获取当前工作目录
current_directory = os.getcwd() + "/yangying"
count = 0
ok_count = 0


def add_to_file_dict(file_dict_: dict, f: dict, path):
    id = f.get('id')
    data_file = file_dict_.get(id) if file_dict_.get(id) else {}
    data_file['id'] = f.get('id', data_file.get('id'))
    data_file['title'] = f.get('title', data_file.get('title'))
    data_file['parentId'] = f.get('parentId', data_file.get('parentId'))
    data_file['answerFlow'] = f.get('answerFlow', data_file.get('answerFlow'))
    data_file['type'] = f.get('type', data_file.get('type'))
    data_file['path'] = path

    file_dict_[id] = data_file


def build_file_dict(json_data, path):
    file_dict_ = {}
    add_to_file_dict(file_dict_, json_data, path)
    children_ = json_data['questions']
    for c in children_:
        add_to_file_dict(file_dict_, c, path)
        for cc in c['questions']:
            add_to_file_dict(file_dict_, cc, path)
            for ccc in cc['questions']:
                add_to_file_dict(file_dict_, ccc, path)
    return file_dict_


def unzip(zip_file_name: str):
    # 指定要解压的 ZIP 文件路径和解压目标路径
    zip_file_path = current_directory + '/' + zip_file_name
    extract_to_folder = current_directory + '/' + zip_file_name[:-4]
    if not os.path.exists(extract_to_folder):
        # 打开 ZIP 文件
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                # 解压 ZIP 文件到目标路径
                zip_ref.extractall(extract_to_folder)
        except Exception as e:
            print("errorZip", zip_file_name)
    return extract_to_folder


def get_root_id(file_dict_, root_id):
    dict_get = file_dict_.get(root_id)
    if dict_get:
        return get_root_id(file_dict_, dict_get['parentId'])
    else:
        return root_id


def get_root_ids(file_dict_):
    root_ids = set()
    for key, value in file_dict_.items():
        root_ids.add(get_root_id(file_dict_, value['parentId']))
    return root_ids


# 遍历数据，建立父子关系
def build_base_question(read_value: dict, param: list, path: str):
    if not param:
        return
    name_list = []
    audio_set = set()
    question_set = set()
    show_score = []

    svg = None
    try:
        for pp in param:
            for p in pp:
                if p['name'] == "playAudio" and len(pp) == 1:
                    if p['valueType'] != 'resource':
                        assert False, "playAudio valueType 不为 resource"
                    read_value['audio'] = p['value']
                    audio_set.add(p['value'])
                elif p['name'] == "wait" and len(pp) == 1:
                    break
                elif p['name'] == "playAudio" and len(pp) == 2:
                    if pp[1]['value'] in ["第一遍", "第二遍"]:
                        break
                    else:
                        assert False, "playAudio 第二个参数不为 第一遍 或 第二遍"
                elif p['name'] == "showTitle":
                    if p['valueType'] != 'string':
                        print("showTitle valueType 不为 string")
                    read_value['question'] = p['value']
                    question_set.add(p['value'])
                elif p['name'] == "showImage":
                    if "img" in read_value:
                        assert False, "showImage 与 showScore 同时存在"
                    read_value['img'] = p['value']
                elif p['name'] == "showOptions":
                    if p['valueType'] == 'matrix':
                        loads = json.loads(p['value'])
                        read_value['items'] = items = []
                        for load in loads:
                            if len(load) != 3:
                                assert False, "showOptions 选项长度有问题"
                            if load[1] and not load[2]:
                                items.append({"text": load[1]})
                            elif load[2] and not load[1]:
                                items.append({"image": load[2]})
                            else:
                                assert False, "showOptions 选型都为空"
                    else:
                        assert False, "showOptions valueType 不为 matrix"
                elif p['name'] == 'showTips' and p['value'] == '请答题':
                    if len(pp) == 1:
                        break
                    elif len(pp) == 2:
                        if pp[1]['name'] == "countdown":
                            break
                        else:
                            assert False, "showTips 第二个参数不为 countdown"
                elif p['name'] == 'countdown' and len(pp) == 2:
                    if pp[1]['value'] == "请答题":
                        break
                    else:
                        assert False, "countdown 第二个参数不为 请答题"
                elif p['name'] == 'finish' and len(pp) == 1:
                    break
                elif p['name'] == 'showScore':
                    if "img" in read_value:
                        assert False, "showImage 与 showScore 同时存在"
                    read_value["img"] = p['value'][:-3] + 'svg'
                    show_score.append(p)
                    continue
                elif p['name'] == 'addFrame':
                    if len(show_score) != 1:
                        exit(-1)
                    score_ = show_score[0]
                    svg_ = score_['value'][:-3] + 'svg'
                    svg_ = svg_.replace("score", "score1")
                    join = os.path.join(path, svg_)
                    frames = json.loads(p['value'])
                    try:
                        svg = get_add_frame_svg(svg, frames, join)
                    except Exception as e:
                        traceback.print_exc()
                        print("errorSvg", frames, join)
                        exit(-2)

                elif p['name'] == 'addIcons' or p['name'] == 'addBeat':
                    if len(show_score) != 1:
                        exit(-1)
                    score_ = show_score[0]
                    svg_ = score_['value'][:-3] + 'svg'
                    svg_ = svg_.replace("score", "score1")
                    join = os.path.join(path, svg_)
                    json_loads = json.loads(p['value'])
                    try:
                        svg = get_add_icon_svg(svg, json_loads, join)
                    except Exception as e:
                        traceback.print_exc()
                        print("errorSvgIcon", json_loads, join)
                        exit(-2)
                elif p['name'] == 'hideElements':
                    if len(show_score) != 1:
                        exit(-1)
                    score_ = show_score[0]
                    svg_ = score_['value'][:-3] + 'svg'
                    svg_ = svg_.replace("score", "score1")
                    join = os.path.join(path, svg_)
                    json_loads = json.loads(p['value'])
                    try:
                        svg = get_svg_and_hide_node(svg, json_loads, join)
                    except Exception as e:
                        traceback.print_exc()
                        print("errorSvgIcon", json_loads, join)
                        exit(-2)

                elif p['name'] == 'addLabels':
                    if len(show_score) != 1:
                        exit(-1)
                    score_ = show_score[0]
                    svg_ = score_['value'][:-3] + 'svg'
                    svg_ = svg_.replace("score", "score1")
                    join = os.path.join(path, svg_)
                    json_loads = json.loads(p['value'])
                    try:
                        svg = get_add_text_svg(svg, json_loads, join)
                    except Exception as e:
                        traceback.print_exc()
                        print("errorSvgIcon", json_loads, join)
                        exit(-2)

                else:
                    assert False, "不支持的参数"
                for pn in pp:
                    name_list.append(pn['name'])

        if svg:
            try:
                path = os.path.join(path, show_score[0]['value'])
                sava_svg(svg, path)
            except Exception as e:
                traceback.print_exc()
                exit(-2)

        if len(audio_set) == 1:
            del read_value['audio']

        assert len(audio_set) <= 2, "audio_set 长度大于1"
        assert len(question_set) <= 1, "question_set 长度大于1"

    except Exception as e:
        traceback.print_exc()
        print(json.dumps(param, ensure_ascii=False, indent=4))
        read_value["support"] = False
        if svg:
            try:
                path = os.path.join(path, show_score[0]['value'])
                sava_svg(svg, path)
            except Exception as e:
                print("errorSaveSvg", svg)
                traceback.print_exc()
                exit(-2)


# 定义一个函数来递归构建层级关系
def build_hierarchy(parent_id_, level):
    if parent_id_ in parent_child_relationship:
        children = parent_child_relationship[parent_id_]
        for child in children:
            child["children"] = build_hierarchy(child["id"], level + 1)
        return children
    return []


if __name__ == '__main__':
    # 遍历当前目录中的所有文件
    zip_files = [file for file in os.listdir(current_directory) if file.endswith('.zip')]

    for zip_file in zip_files:
        unzip_file_path = unzip(zip_file)
        print("读取文件：", os.path.join(unzip_file_path))
        with open(os.path.join(unzip_file_path, "data.json"), "r") as f:
            file_dict = build_file_dict(json.loads(f.read()), unzip_file_path)

        # 创建一个字典用于存储父子关系
        parent_child_relationship = {}

        for key, value in file_dict.items():
            parent_id = value["parentId"]
            if parent_id not in parent_child_relationship:
                parent_child_relationship[parent_id] = []

            # 复制./score 到 ./score1
            if not os.path.exists(value['path'] + "/" + "score1"):
                shutil.copytree(value['path'] + "/" + "score", value['path'] + "/" + "score1")

            read_value = {
                'id': value['id'],
                'question': value['title'],
                'type': value['type'],
                'answerFlow': value['answerFlow'],
            }
            # 构建问题信息
            build_base_question(read_value, value['answerFlow'], value['path'])
            parent_child_relationship[parent_id].append(read_value)

        root_ids = get_root_ids(file_dict)

        for root_id in root_ids:
            # 构建整个层级关系
            hierarchy = build_hierarchy(root_id, 0)

            # 将层级关系写入文件
            with open(os.path.join(unzip_file_path, "my-data.json"), "w") as f:
                f.write(json.dumps(hierarchy, indent=4, ensure_ascii=False))
