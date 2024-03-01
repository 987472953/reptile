import json

from py.download import upload_file

upload = False

if __name__ == '__main__':
    count_dict = {}
    # base_url = '/Users/mac/Downloads/lv'
    base_url = '/Users/mac/Downloads/jz'
    with open('%s/data.json' % base_url, 'r', encoding="utf-8") as f:
        # 读取文件内容
        loads = json.loads(f.read())
        nodes_ = loads['data'][0]['nodes']
        count_dict = {}
        try:
            for node in nodes_:
                print(node)
                node['group'] = node['kpCls'] if 'kpCls' in node else node['tune']
                if "url" in node:
                    continue
                attach_xmls = node['attach']['xmls']
                xmls_ = base_url + "/" + attach_xmls[0]
                json_path = xmls_[:-4] + ".json"
                # 上传文件
                if upload:
                    node['url'] = upload_file(json_path, biz="music_knowledge_yingke_test", appId="286")
        except Exception as e:
            with open('%s/data1.json' % base_url, 'w', encoding="utf-8") as f2:
                f2.write(json.dumps(loads, ensure_ascii=False))

        with open('%s/data1.json' % base_url, 'w', encoding="utf-8") as f2:
            f2.write(json.dumps(loads, ensure_ascii=False))
        print(count_dict)