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
        file_name = str(title) + ".zip"
        # 如果文件存在 添加UUID
        if os.path.exists(file_name):
            file_name = str(title) + ":" + str(uuid.uuid4()) + ".zip"
        with open(file_name, "wb") as file:
            for chunk in download_response.iter_content(chunk_size=8192):
                file.write(chunk)
        print("Download completed.")
    else:
        print("Download failed. Status code:", download_response.status_code)
