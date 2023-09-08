import json
import traceback
import zipfile
import os

from py.央音svg import get_add_frame_svg, get_add_icon_svg, sava_svg

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


def build_file_dict(file_dict_, json_data, path):
    add_to_file_dict(file_dict_, json_data, path)
    children_ = json_data['questions']
    for c in children_:
        add_to_file_dict(file_dict_, c, path)
        for cc in c['questions']:
            add_to_file_dict(file_dict_, cc, path)
            for ccc in cc['questions']:
                add_to_file_dict(file_dict_, ccc, path)

    # print(json.dumps(file_dict_, indent=4, ensure_ascii=False))


def unzip(zip_file_i: str):
    # 指定要解压的 ZIP 文件路径和解压目标路径
    zip_file_path = current_directory + '/' + zip_file_i
    extract_to_folder = current_directory + '/' + zip_file_i[:-4]
    if not os.path.exists(extract_to_folder):
        # 打开 ZIP 文件
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # 解压 ZIP 文件到目标路径
            zip_ref.extractall(extract_to_folder)
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
def build_base_question(read_value: dict, param: list, path):
    global count, ok_count
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
                        print("playAudio valueType 不为 resource")
                        assert False
                    read_value['audio'] = p['value']
                    audio_set.add(p['value'])
                elif p['name'] == "wait" and len(pp) == 1:
                    break
                elif p['name'] == "playAudio" and len(pp) == 2:
                    if pp[1]['value'] in ["第一遍", "第二遍"]:
                        break
                    else:
                        assert False
                elif p['name'] == "showTitle":
                    if p['valueType'] != 'string':
                        print("showTitle valueType 不为 string")
                    read_value['question'] = p['value']
                    question_set.add(p['value'])
                elif p['name'] == "showImage":
                    if "img" in read_value:
                        assert False
                    read_value['img'] = p['value']
                elif p['name'] == "showOptions":
                    if p['valueType'] == 'matrix':
                        loads = json.loads(p['value'])
                        read_value['items'] = items = []
                        for load in loads:
                            if load[1] and not load[2]:
                                items.append({"text": load[1]})
                            elif load[2] and not load[1]:
                                items.append({"image": load[2]})
                            else:
                                assert False
                            if len(load) != 3:
                                assert False
                    else:
                        assert False
                elif p['name'] == 'showTips' and p['value'] == '请答题':
                    if len(pp) == 1:
                        break
                    elif len(pp) == 2:
                        if pp[1]['name'] == "countdown":
                            break
                        else:
                            assert False
                elif p['name'] == 'finish' and len(pp) == 1:
                    break
                elif p['name'] == 'showScore':
                    if "img" in read_value:
                        assert False
                    read_value["img"] = p['value'][:-3] + 'svg'
                    show_score.append(p)
                    continue
                elif p['name'] == 'addFrame':
                    if len(show_score) != 1:
                        exit(-1)
                    score_ = show_score[0]
                    join = os.path.join(path, score_['value'][:-3] + 'svg')
                    frames = json.loads(p['value'])
                    try:
                        svg = get_add_frame_svg(svg, frames, join)
                        read_value["img"] = read_value['img'][:-4] + '-new.svg'
                    except Exception as e:
                        traceback.print_exc()
                        print("errorSvg", frames, join)
                elif p['name'] == 'addIcons':
                    if len(show_score) != 1:
                        exit(-1)
                    score_ = show_score[0]
                    join = os.path.join(path, score_['value'][:-3] + 'svg')
                    json_loads = json.loads(p['value'])
                    try:
                        svg = get_add_icon_svg(svg, json_loads, join)
                    except Exception as e:
                        traceback.print_exc()
                        print("errorSvgIcon", json_loads, join)
                elif p['name'] == 'showTips' and p['value'] == '请答题' and len(pp) == 2:
                    if pp[1]['name'] == "countdown":
                        break
                    else:
                        assert False
                elif p['name'] == 'countdown' and len(pp) == 2:
                    if pp[1]['value'] == "请答题":
                        break
                    else:
                        assert False
                else:
                    print(p)
                    assert False
                for pn in pp:
                    name_list.append(pn['name'])

        if svg:
            try:
                path = os.path.join(path, show_score[0]['value'])
                sava_svg(svg, path)
            except Exception as e:
                traceback.print_exc()
                exit(-2)

        assert len(audio_set) <= 2, "audio_set 长度大于1"
        assert len(question_set) <= 1, "question_set 长度大于1"

    except Exception as e:
        # traceback.print_exc()
        # print(json.dumps(param, ensure_ascii=False, indent=4))
        read_value["support"] = False
        if svg:
            try:
                path = os.path.join(path, show_score[0]['value'])
                sava_svg(svg, path)
            except Exception as e:
                print("errorSaveSvg", svg)
                traceback.print_exc()
                exit(-2)

        # exit(1)
    # # # elements_to_check = ["record", "recordRhythm", "addBeat", "showDrum", "addFrame", "showScore"]
    # elements_to_check = ["addFrame"]
    #
    # hava = False
    # # for element in elements_to_check:
    # #     if element in name_list:
    # #         hava = True
    # #         break
    # if "addFrame" in name_list and "showScore" not in name_list:
    #     hava = True
    #
    # if hava:
    #     count += 1
    # else:
    #     ok_count += 1


# 定义一个函数来递归构建层级关系
def build_hierarchy(parent_id_, level):
    if parent_id_ in parent_child_relationship:
        children = parent_child_relationship[parent_id_]
        for child in children:
            child["children"] = build_hierarchy(child["id"], level + 1)
        return children
    return []


# 遍历当前目录中的所有文件
zip_files = [file for file in os.listdir(current_directory) if file.endswith('.zip')]

for zip_file in zip_files:
    file_dict = {}
    unzip_file_path = unzip(zip_file)
    with open(os.path.join(unzip_file_path, "data.json"), "r") as f:
        build_file_dict(file_dict, json.loads(f.read()), unzip_file_path)

    # 创建一个字典用于存储父子关系
    parent_child_relationship = {}

    options_set = set()

    for key, value in file_dict.items():
        parent_id = value["parentId"]
        if parent_id not in parent_child_relationship:
            parent_child_relationship[parent_id] = []

        read_value = {
            'id': value['id'],
            'question': value['title'],
            'type': value['type'],
        }
        build_base_question(read_value, value['answerFlow'], value['path'])
        read_value['answerFlow'] = value['answerFlow']
        if "supportr " in read_value:
            continue
        parent_child_relationship[parent_id].append(read_value)
    # print(parent_child_relationship)

    root_ids = get_root_ids(file_dict)
    # print(root_ids)

    for root_id in root_ids:
        # 构建整个层级关系
        hierarchy = build_hierarchy(root_id, 0)

        # 将层级关系写入文件
        with open(os.path.join(unzip_file_path, "my-data.json"), "w") as f:
            f.write(json.dumps(hierarchy, indent=4, ensure_ascii=False))
