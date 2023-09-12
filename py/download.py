import os
import uuid

import requests

headers = {
    "Host": "xl.kaoji.com",
    "Cookie": "acw_tc=0b32974216929332715483135e030877dce01e91ee15093ae37e298e6c96dd",
    "accept": "*/*",
    "user-agent": "MusicApp/57 CFNetwork/1410.0.3 Darwin/22.6.0",
    "accept-language": "zh-CN,zh-Hans;q=0.9",
}

downloadUrl = "https://xl.kaoji.com/exercise//rest/exam/downloadExerciseZip"


def downloadFile(id, title):
    download_params = {
        'exercisePurchasedId': id,
        'accessToken': 'OTJhZTFiOGI3NjA4NDllZWI4OWNmNTc0ZWU2ZTIyYjA='
    }
    download_response = requests.get(downloadUrl, headers=headers, params=download_params, stream=True)
    if download_response.status_code == 200:
        # 如果返回的是json
        if download_response.headers.get("Content-Type") == "application/json;charset=UTF-8":
            print(download_response.content.decode("utf-8"))
            return
        if len(download_response.content) < 100:
            print(download_response.content.decode("utf-8"))
            return
        print("Downloading...")
        file_name = "yangying/" + str(title) + ".zip"
        # 如果文件存在 添加UUID
        if os.path.exists(file_name):
            file_name = str(title) + ":" + str(uuid.uuid4()) + ".zip"
        with open(file_name, "wb") as file:
            for chunk in download_response.iter_content(chunk_size=8192):
                file.write(chunk)
        print("Download completed.")
    else:
        print("Download failed. Status code:", download_response.status_code)


def upload_file(file_path):
    url = "https://image-d.quthing.com/oss/file/upload"
    headers = {
        "Authorization": "Token 00a8ab11d35851a99bef97f2e991bb0e05fce268"
    }

    payload = {
        "biz": "music_knowledge_exam_test",
        "appId": "286"
    }

    files = {
        "file": (file_path.split("/")[-1],
                 open(file_path, "rb"))
    }

    response = requests.post(url, headers=headers, data=payload, files=files)

    print(response.status_code)
    print(response.text)
    json = response.json()
    return json['data'][0]['url']
