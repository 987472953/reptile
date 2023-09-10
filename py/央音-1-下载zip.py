import json

import requests

from py.download import downloadFile

url = "https://xl.kaoji.com/exercise/rest/exam/menuUnits"

headers = {
    "Host": "xl.kaoji.com",
    "Cookie": "acw_tc=0b32974616928481874132571eec736ed4ace4862e83550a2e4f7c9ff51373",
    "accept": "application/json, text/plain, */*",
    "x-custom-header": "foobar",
    "user-agent": "MusicApp/57 CFNetwork/1410.0.3 Darwin/22.6.0",
    "accept-language": "zh-CN,zh-Hans;q=0.9",
    "accesstoken": "OTJhZTFiOGI3NjA4NDllZWI4OWNmNTc0ZWU2ZTIyYjA=",
}
proxies = {
    'http': "http://127.0.0.1:7890",
    'https': "http://127.0.0.1:7890",
}


def build_my_data(file_dict: dict, f: dict):
    fid = f['fId']
    data_file = file_dict.get(fid) if file_dict.get(fid) else {}
    data_file['id'] = f.get('fId', data_file.get('id'))
    data_file['title'] = f.get('fTitle', data_file.get('title'))
    data_file['enTitle'] = f.get('fEntitle', data_file.get('enTitle'))
    data_file['rootId'] = f.get('fRootId', data_file.get('rootId'))
    data_file['parentId'] = f.get('fParentId', data_file.get('parentId'))
    data_file['level'] = f.get('fLevel', data_file.get('level'))
    data_file['questionId'] = f.get('fQuestionId', data_file.get('questionId'))
    data_file['question'] = f.get('question', data_file.get('question'))
    data_file['free'] = f.get('fFree', data_file.get('free'))

    file_dict[fid] = data_file


def get_and_download_zip(menuId: int, level: str):
    file_dict = {}
    params = {
        'menuId': menuId
    }

    response = requests.post(url, headers=headers, params=params, stream=True, proxies=proxies)
    print("请求结果-----------------")
    print(response.text)
    print("请求结果-----------------")
    if response.status_code == 200:
        json_data = response.json()
        for data in json_data['data']:
            build_my_data(file_dict, data)
            children_ = data['children']
            for c in children_:
                build_my_data(file_dict, c)
                for cc in c['children']:
                    build_my_data(file_dict, cc)
                    commodity_ = cc['commodity']
                    build_my_data(file_dict, commodity_)

    else:
        print("Request failed. Status code:", response.status_code)
    print("result json-----------------")
    print(json.dumps(file_dict, indent=4, ensure_ascii=False))
    print("result json-----------------")
    for value in file_dict.values():
        downloadFile(value['id'], level + value['title'])


get_and_download_zip(menuId=3, level="初级")
get_and_download_zip(menuId=7, level="中级")
get_and_download_zip(menuId=10, level="高级")
# get_and_download_zip(1)
# get_and_download_zip(5)
# get_and_download_zip(9)


#
# # 创建一个字典用于存储父子关系
# parent_child_relationship = {}
#
# # 遍历数据，建立父子关系
# for key, value in file_dict.items():
#     parent_id = value["parentId"]
#     if parent_id not in parent_child_relationship:
#         parent_child_relationship[parent_id] = []
#
#     read_value = {}
#     read_value["id"] = value["id"]
#     read_value["title"] = value["title"]
#     read_value["enTitle"] = value["enTitle"]
#     read_value["subTitle"] = value["title"]
#     read_value["indexTitle"] = value["title"]
#     read_value["isMoNi"] = True
#     read_value["count"] = 0
#     parent_child_relationship[parent_id].append(read_value)
# print(parent_child_relationship)

# 定义一个函数来递归构建层级关系
# def build_hierarchy(parent_id, level):
#     if parent_id in parent_child_relationship:
#         children = parent_child_relationship[parent_id]
#         for child in children:
#             child["children"] = build_hierarchy(child["id"], level + 1)
#         return children
#     return []
#
# # 构建整个层级关系
# root_id = 36  # 根节点的 parent_id 为 None
# hierarchy = build_hierarchy(root_id, 0)
# print()
# print()
# print(json.dumps(hierarchy, indent=4, ensure_ascii=False))
