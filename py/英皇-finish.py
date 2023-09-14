import json
import os
import zipfile

from py.download import upload_file

current_directory = os.getcwd() + "/yinghuang"

items = os.listdir(current_directory)

# 使用os.path.isdir检查每个项是否是目录
subdirectories = [item for item in items if os.path.isdir(os.path.join(current_directory, item)) and item != "origin"]
# 打印所有一级目录
title_dict = {
    'title': "英国皇家音乐学院",
    'image': 'img_center',
    'entitys': []
}

for subdirectory in subdirectories:

    id = subdirectory
    print(id)
    count = 0
    with open(os.path.join(current_directory, subdirectory, "data.json"), 'r',
              encoding='utf-8') as f:
        loads = json.loads(f.read())
        count = len(loads)
    exam_param = {
        "title": "Grade " + subdirectory[-1:],
        "isVIP": True,
        "id": id,
        "count": count,
        "subTitle": "Music Theory Sample Paper",
        "indexTitle": "Grade " + subdirectory[-1:],
        "index":  int(subdirectory[-1:]),
        "isMoNi": True,
        "source": ""
    }

    new_path = os.path.join(current_directory, id)
    folder_to_compress = new_path
    zip_file_path = new_path + ".zip"
    print(zip_file_path)
    if os.path.exists(zip_file_path):
        os.remove(zip_file_path)
    # 压缩后的 ZIP 文件路径
    # 创建一个 ZIP 文件
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历文件夹中的所有文件和子文件夹，并将它们添加到 ZIP 文件中
        for root, _, files in os.walk(folder_to_compress):
            for file in files:
                if file.endswith('.json') and (
                        not file.endswith("data.json") and not file.endswith("resource.json")):
                    continue
                if file.endswith("my-data.json"):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_to_compress)
                zipf.write(file_path, arcname)

    try:
        url = upload_file(zip_file_path)
        exam_param['source'] = url
    except Exception as e:
        print("errorUploadFile", zip_file_path)
    title_dict['entitys'].append(exam_param)

sorted_data = sorted(title_dict['entitys'], key=lambda x: x["index"])
title_dict['entitys'] = sorted_data
for v in sorted_data:
    del v['index']
print(json.dumps(title_dict, ensure_ascii=False, indent=4))
