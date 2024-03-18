import logging
from time import sleep
from urllib.parse import quote

import requests

logging.captureWarnings(True)

import http.cookies

private_token = 'sBnNpMooyiz4fs5HJx15'

cookie_str = 'sidebar_collapsed=false; cna=a85df3c215164d3a80b05d8f12131bf9; mis-token=d076c39c-9fd8-4f5f-b4a6-cdd213ef4719; known_sign_in=djZVYW84emdZNTMybENxTk5YUlJ4UGp5RExpR09rSVdLdFVPV3VNRFdtNmlmbS9uK2VWL0NnRVdiemkxNS93eW1jelNpODZ3L0Q0TWRUeHJRNmF1ZWV5NkliNmNrd3UwZ2JTc1dlVFlXM1lBNXN5aVNNbGFKVUc2bWV3NzB5VGktLVlNb1ZGT3JpYUJ3czhJSDVUTWlnL3c9PQ%3D%3D--94b2d5fb892113ae588c272a137ec3acdc33b10b; _gitlab_session=fd76ba0747190708eadfbf7b59c4a911; mis-token-dev=9c0db972-1edd-4eed-aa5e-8f32d7e365e9'

cookie = http.cookies.SimpleCookie()
cookie.load(cookie_str)
cookie_dict = {}
for key, morsel in cookie.items():
    cookie_dict[key] = morsel.value


# 获取树的结构
def get_tree(project_id, path):
    api_url = f"{gitlab_base_url}/api/v4/projects/{project_id}/repository/tree?path={path}"
    print(api_url)
    headers = {'Private-Token': private_token}
    response = requests.get(api_url, headers=headers, verify=False)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"获取文件树失败：{response.status_code}")
        print(response.text)
        return []


# 获取文件内容
def get_file_content(project_id, file_path):
    api_url = f"{gitlab_base_url}/api/v4/projects/{project_id}/repository/files/{quote(file_path, safe='')}/raw?ref=master"
    print(api_url)
    headers = {'Private-Token': private_token}
    response = requests.get(api_url, headers=headers, verify=False)

    if response.status_code == 200:
        file_content = response.text
        print(f"文件路径：{file_path}")
        print(f"文件内容：{file_content}")
    else:
        print(f"获取文件内容失败：{response.status_code}")
        print(response.text)


# 递归遍历文件树
def traverse_tree(tree, project_id):
    for item in tree:
        if item['type'] == 'tree':
            # 处理目录
            traverse_tree(get_tree(project_id, item['path']), project_id)
        else:
            # 处理文件
            file_path = item['path']
            get_file_content(project_id, file_path)


def traverse_gitlab_urls(base_url):
    page = 1
    per_page = 1000
    url_count = 0

    while True:
        # 发起GitLab API请求获取URL列表
        api_url = f"{base_url}/api/v4/projects?order_by=id&sort=asc&per_page={per_page}&page={page}"
        print(api_url)
        response = requests.get(api_url, verify=False, cookies=cookie_dict)

        if response.status_code == 200:
            projects = response.json()

            if len(projects) == 0:
                break

            for project in projects:
                project_id = project["id"]
                project_name = project["name"]
                project_url = f"{base_url}/{project_name}"

                print(f"项目名称：{project_name}")
                print(project)

                # download_git_repository(project_id)
                get_file_raw(base_url, project_id)
                # sleep(30)

            page += 1
        else:
            print(f"Error: Failed to fetch projects from GitLab API. Status Code: {response.status_code}")
            break

    print(f"Total URLs found: {url_count}")


def get_file_raw(base_url, project_id):
    # 获取项目的文件列表
    tree_api_url = f"{base_url}/api/v4/projects/{project_id}/repository/tree"
    response = requests.get(tree_api_url, verify=False, cookies=cookie_dict)
    print(tree_api_url)
    if response.status_code == 200:
        files = response.json()
        traverse_tree(files, project_id)
    else:
        print(f"获取项目文件列表失败：{response.status_code}")
        print(response.text)


# 下载 Git 仓库的代码
def download_git_repository(project_id):
    api_url = f"{gitlab_base_url}/api/v4/projects/{project_id}/repository/archive"
    headers = {'Private-Token': private_token}

    response = requests.get(api_url, headers=headers, stream=True)

    if response.status_code == 200:
        # 保存下载的代码到本地文件
        with open(f'repository/{project_id}.zip', 'wb') as file:
            for chunk in response.iter_content(chunk_size=128):
                file.write(chunk)
        print("代码下载完成")
    else:
        print(f"无法下载代码：{response.status_code}")
        print(response.text)


# 使用您的GitLab实例URL调用函数
gitlab_base_url = "https://gitlab.quthing.com"
traverse_gitlab_urls(gitlab_base_url)
