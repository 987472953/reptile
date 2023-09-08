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
# 1 5 9



def get(menuId, level):
    file_dict = {}
    params = {
        'menuId': menuId
    }

    def method_name(file_dict: dict, f: dict):
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
        # data_file['commodity'] = f.get('commodity', data_file.get('commodity'))
        data_file['free'] = f.get('fFree', data_file.get('free'))

        file_dict[fid] = data_file

    response = requests.post(url, headers=headers, params=params, stream=True, proxies=proxies)
    print(response.text)
    file = {
        'id': 1,
        'type': 1,
        'parentId': 1,
        'rootId': 1,
        'title': 'test',
        'questionId': 1,
        'commodityId': 1,
        'level': 1,
        'commodity': {},
        'question': {},
        'free': 1
    }
    if response.status_code == 200:
        json_data = response.json()
        # print(json_data)
        for data in json_data['data']:
            method_name(file_dict, data)
            children_ = data['children']
            for c in children_:
                method_name(file_dict, c)
                for cc in c['children']:
                    method_name(file_dict, cc)
                    commodity_ = cc['commodity']
                    # print(commodity_)
                    method_name(file_dict, commodity_)

                    # commodityId = commodity_['fId']
                    # commodityTitle = commodity_['fPayTitle']
                    # commodityEnTitle = commodity_['fEntitle']
                    # if not cc['children']:
                    #     print(cc['children'])
                    # if not cc['question']:
                    #     print(cc['question'])
                    # if not cc['exerciseOnlineList']:
                    #     print(cc['exerciseOnlineList'])

    else:
        print("Request failed. Status code:", response.status_code)
    print(json.dumps(file_dict, indent=4, ensure_ascii=False))
    for value in file_dict.values():
        downloadFile(value['id'],level+ value['title'])





# get(3, "初级")
# get(7, "中级")
get(10, "高级")
# get(1)
# get(5)
# get(9)



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