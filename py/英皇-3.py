import json
import os


def get_all_resource_paths(directory):
    resource_paths = []

    # 使用 os.walk 遍历文件夹及其子文件夹
    for root, _, files in os.walk(directory):
        for file in files:
            if file == '.DS_Store':
                continue
            # 获取资源的绝对路径
            resource_path = os.path.join(root, file)
            # 使用 os.path.relpath 获取相对路径
            relative_path = os.path.relpath(resource_path, start=directory)
            resource_paths.append(relative_path)

    return resource_paths


index = 5
with open('yinghuang/{}/data.json'.format(index,index), 'r') as f:
    loads = json.loads(f.read())
    # 遍历loads 如果loads['type'] != 'question' 则删除
    filtered_list = [item for item in loads if item['type'] == '[ 单选 ] ']
    with open('yh_music_theory_sample_paper_2020_grade_{}/data.json'.format(index), 'w') as ff:
        ff.write(json.dumps(filtered_list, indent=4, ensure_ascii=False))

with open('yh_music_theory_sample_paper_2020_grade_{}/resource.json'.format(index), 'w+') as f:
    resource = {}
    # 遍历获得 ./yh_music_theory_sample_paper_2020_grade_1 下面所有资源的路径
    paths = get_all_resource_paths('yh_music_theory_sample_paper_2020_grade_{}'.format(index))
    resource['list'] = paths

    f.write(json.dumps(resource, indent=4, ensure_ascii=False))
