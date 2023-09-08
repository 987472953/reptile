# 打开yangying文件夹 遍历
import json
import os
import re
import shutil
import zipfile

current_directory = os.getcwd() + "/yangying"

# for root, dirs, files in os.walk(current_directory):
#     for file in files:
#         if file.endswith('my-data-answer.json'):
#             # 打开文件
#             with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
#                 # 读取文件内容
#                 json_data = json.load(f)
#                 # 获取文件夹名
#                 print(json_data[0]['children'])
#                 # 获取文件questions的长度
#                 support_list = []
#                 no_support_list = []
#                 for child in json_data[0]['children']:
#                     if child['type'] == '1':
#                         child['type'] = '[ 单选 ] '
#                     else:
#                         child['type'] = '[ 未知 ] '
#                     # 将support为false的题目放到另一个文件
#                     if 'support' in child and child['support'] == False:
#                         no_support_list.append(child)
#                     else:
#                         del child["answerFlow"]
#                         del child["children"]
#                         support_list.append(child)
#                 with open(os.path.join(root, file[:-5] + "-support.json"), 'w', encoding='utf-8') as f:
#                     f.write(json.dumps(support_list, indent=4, ensure_ascii=False))
#                 with open(os.path.join(root, file[:-5] + "-no-support.json"), 'w', encoding='utf-8') as f:
#                     f.write(json.dumps(no_support_list, indent=4, ensure_ascii=False))


chinese_int_list = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
english_int_list = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
int_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

level_dict = {
    '初级': 'primary',
    '中级': 'intermediate',
    '高级': 'advanced',
    '常识': 'cs',
}
items = os.listdir(current_directory)

# 使用os.path.isdir检查每个项是否是目录
subdirectories = [item for item in items if os.path.isdir(os.path.join(current_directory, item))]

index_list = []
title_dict = {}
title_set = set()
# 打印所有一级目录
for subdirectory in subdirectories:
    title_set.add(subdirectory[:2])
for title in title_set:
    for subdirectory in subdirectories:
        if subdirectory.startswith(title):
            if title not in title_dict:
                title_dict[title] = {
                    'title': subdirectory[:-3],
                    'entitys': []
                }
            index = 0
            if subdirectory[-2:-1] in chinese_int_list:
                index = chinese_int_list.index(subdirectory[-2:-1])
            count = 0
            with open(os.path.join(current_directory, subdirectory, "my-data-answer-support.json"), 'r',
                      encoding='utf-8') as f:
                loads = json.loads(f.read())
                count = len(loads)

            id = level_dict[title] + "_integrated_simulation_" + english_int_list[index]
            print(id)
            title_dict[title]['entitys'].append({
                "title": subdirectory[:-3] + " " + str(int_list[index]),
                "isVIP": True,
                "id": id,
                "count": count,
                "subTitle": subdirectory[:-3] + " " + str(int_list[index]),
                "indexTitle": subdirectory[2:],
                "index": int_list[index],
                "isMoNi": True,
                "source": "https://cdn.quthing.com/c703bc99-8d9e-4964-9b65-c9e4155f056b.zip"
            })
            old_path = os.path.join(current_directory, subdirectory)
            new_path = os.path.join(current_directory, id)
            rename = os.rename(old_path, new_path)
            rename = os.rename(new_path + '/data.json', new_path + "/data1.json")
            rename = os.rename(new_path + "/my-data-answer-support.json", new_path + '/data.json')

            folder_to_compress = new_path
            # 压缩后的 ZIP 文件路径
            zip_file_path = new_path + ".zip"
            # 创建一个 ZIP 文件
            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 遍历文件夹中的所有文件和子文件夹，并将它们添加到 ZIP 文件中
                for root, _, files in os.walk(folder_to_compress):
                    for file in files:
                        if file.endswith('.json') and file.endswith("my-data.json") and (
                                not file.endswith("data.json") and not file.endswith("resource.json")):
                            continue
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, folder_to_compress)
                        zipf.write(file_path, arcname)
            rename = os.rename(new_path + '/data.json', new_path + "/my-data-answer-support.json")
            rename = os.rename(new_path + "/data1.json", new_path + '/data.json')
            rename = os.rename(new_path, old_path)

for key, value in title_dict.items():
    entitys_ = value['entitys']
    sorted_data = sorted(entitys_, key=lambda x: x["index"])
    value['entitys'] = sorted_data
    for v in sorted_data:
        del v['index']
    print(json.dumps(value, ensure_ascii=False, indent=4))
