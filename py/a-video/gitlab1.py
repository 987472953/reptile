import os

import gitlab
import logging
logging.captureWarnings(True)

# 代理配置
proxy_host = '127.0.0.1'  # 代理主机
proxy_port = 50944  # 代理端口

# 设置环境变量
os.environ['HTTP_PROXY'] = f'http://{proxy_host}:{proxy_port}'
os.environ['HTTPS_PROXY'] = f'http://{proxy_host}:{proxy_port}'

# GitLab 访问凭证
# 统计的域名
DOMAIN = 'cdn.quthing.com'

# 创建 GitLab 连接
gl = gitlab.Gitlab.from_config('kaishugit', ['gitlab.cfg'])

gl.auth()

# 获取所有项目
projects = gl.projects.list(all=True)

# 遍历项目
for project in projects:
    print(f"Project: {project.name}")

    # 获取项目中的文件
    files = project.repository_tree(all=True)

    # 遍历文件
    for file in files:
        if file['type'] == 'blob' and DOMAIN in file['path']:
            print(f"URL: {file['path']}")