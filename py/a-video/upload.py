import os
import re
import uuid
import sqlite3
from datetime import datetime

# 设置数据库连接
db_path = 'your_database.db'  # 替换为实际的数据库文件路径
conn = sqlite3.connect(db_path)
cursor = conn.cursor()


def insert_into_table(title, chapter, type, url, extra):
    # 插入数据
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql_statement = f'''
         INSERT INTO course_outline (title, chapter, type, url, extra, cts, uts)    
         VALUES ('{title}', '{chapter}', '{type}', '{url}', '{extra}', '{now}', '{now}');
     '''
    print(sql_statement)

def replace_multiple_spaces(text):
    return re.sub(r'\s+', ' ', text)

def rename_and_insert(folder_path):
    # 获取文件夹下的所有视频文件
    video_files = [f for f in os.listdir(folder_path) if f.endswith(('.mp4', '.avi', '.mkv'))]

    # 创建表格
    for video_file in video_files:
        # 生成UUID作为新的文件名
        new_filename = str(uuid.uuid4()) + os.path.splitext(video_file)[1]

        # 构建文件的绝对路径
        old_filepath = os.path.join(folder_path, video_file)
        new_filepath = os.path.join(folder_path, new_filename)

        # 重命名文件
        os.rename(old_filepath, new_filepath)

        split___ = video_file.rsplit(".", 1)[0]
        spaces = replace_multiple_spaces(split___).strip()
        ch = video_file.split(".")[0]
        # 插入到数据库
        insert_into_table(spaces, ch, '1', "https://cdn.quthing.com/vip/course/dading/2/" + new_filename, '')


if __name__ == "__main__":
    folder_path = '/Users/mac/Downloads/吉他课件/3'  # 替换为实际的文件夹路径
    rename_and_insert(folder_path)

