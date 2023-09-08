# 打开yangying文件夹 遍历
import json
import os

current_directory = os.getcwd() + "/yangying"


def init(id):
    import requests

    url = "https://xl.kaoji.com/exercise/rest/exam/initAnswerExerciseId?unitId={}".format(id)
    headers = {
        "Host": "xl.kaoji.com",
        "Cookie": "acw_tc=0a099d3616941414724555331e9221842bacdd2e4d042d8a8ce781c6ddb37a",
        "accept": "application/json, text/plain, */*",
        "x-custom-header": "foobar",
        "user-agent": "MusicApp/57 CFNetwork/1410.0.3 Darwin/22.6.0",
        "accept-language": "zh-CN,zh-Hans;q=0.9",
        "accesstoken": "OTJhZTFiOGI3NjA4NDllZWI4OWNmNTc0ZWU2ZTIyYjA=",
    }

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        print("init Request successful!")
        # 处理响应内容，例如：
        # print(response.text)
    else:
        print(f"Request failed with status code {response.status_code}")

def do_answer(unitId, questionId):
    import requests
    import json

    url = "https://xl.kaoji.com/exercise/rest/exam/answer"
    headers = {
        "Host": "xl.kaoji.com",
        "Cookie": "acw_tc=0a099d3616941414724555331e9221842bacdd2e4d042d8a8ce781c6ddb37a",
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json;charset=utf-8",
        "x-custom-header": "foobar",
        "user-agent": "MusicApp/57 CFNetwork/1410.0.3 Darwin/22.6.0",
        "accept-language": "zh-CN,zh-Hans;q=0.9",
        "accesstoken": "OTJhZTFiOGI3NjA4NDllZWI4OWNmNTc0ZWU2ZTIyYjA=",
    }

    data = {
        "answer": "",
        "questionId": questionId,
        "unitId": unitId,
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print("do_answer Request successful!")
        # 处理响应内容，例如：
        # print(response.text)
    else:
        print(f"Request failed with status code {response.status_code}")


def save_answer(unitId):
    import requests

    url = "https://xl.kaoji.com/exercise/rest/exam/save?unitId={}".format(unitId)

    headers = {
        "Host": "xl.kaoji.com",
        "Cookie": "acw_tc=0a099d3616941414724555331e9221842bacdd2e4d042d8a8ce781c6ddb37a",
        "accept": "application/json, text/plain, */*",
        "x-custom-header": "foobar",
        "user-agent": "MusicApp/57 CFNetwork/1410.0.3 Darwin/22.6.0",
        "accept-language": "zh-CN,zh-Hans;q=0.9",
        "accesstoken": "OTJhZTFiOGI3NjA4NDllZWI4OWNmNTc0ZWU2ZTIyYjA=",
    }

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        print("save_answer Request successful!")
        # 处理响应内容，例如：
        print(response.text)
    else:
        print(response.text)
        print(f"Request failed with status code {response.status_code}")


def get_answer(unitId):
    import requests

    url = "https://xl.kaoji.com/exercise/rest/exam/lastAnswerDetail?unitId={}".format(unitId)

    headers = {
        "Host": "xl.kaoji.com",
        "Cookie": "acw_tc=0a099d3616941414724555331e9221842bacdd2e4d042d8a8ce781c6ddb37a",
        "accept": "application/json, text/plain, */*",
        "x-custom-header": "foobar",
        "user-agent": "MusicApp/57 CFNetwork/1410.0.3 Darwin/22.6.0",
        "accept-language": "zh-CN,zh-Hans;q=0.9",
        "accesstoken": "OTJhZTFiOGI3NjA4NDllZWI4OWNmNTc0ZWU2ZTIyYjA="
    }

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        # 处理响应内容
        return response.json()
    else:
        print("请求失败，HTTP状态码:", response.status_code)

def get(unitId):
    import requests

    url = "https://xl.kaoji.com/exercise/rest/exam/answerUnits?unitId={}".format(unitId)

    headers = {
        "Host": "xl.kaoji.com",
        "Cookie": "acw_tc=0a099d3616941414724555331e9221842bacdd2e4d042d8a8ce781c6ddb37a",
        "accept": "application/json, text/plain, */*",
        "x-custom-header": "foobar",
        "user-agent": "MusicApp/57 CFNetwork/1410.0.3 Darwin/22.6.0",
        "accept-language": "zh-CN,zh-Hans;q=0.9",
        "accesstoken": "OTJhZTFiOGI3NjA4NDllZWI4OWNmNTc0ZWU2ZTIyYjA="
    }

    response = requests.post(url, headers=headers, data="")

    if response.status_code == 200:
        # 处理响应内容
        json_data = response.json()
        print(json_data)
    else:
        print("请求失败，HTTP状态码:", response.status_code)


for root, dirs, files in os.walk(current_directory):
    for file in files:
        # 如果文件名3为my-data.json
        if file[-13:] == 'my-data.json':
            # 打开文件
            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                # 读取文件内容
                json_data = json.load(f)
                init(json_data[0]['id'])

                for child in json_data[0]['children']:
                    do_answer(json_data[0]['id'], child['id'])

                save_answer(json_data[0]['id'])
                get(json_data[0]['id'])
                answer = get_answer(json_data[0]['id'])

                for a in answer['data']:
                    print(a['exercisePurchased']['question']['props'])
                    for prop in a['exercisePurchased']['question']['props']:
                        if prop['fKey'] == 'correctAnswer':
                            a['fAnswer'] = prop['fValue']
                    for child in json_data[0]['children']:
                        if a['fExerciseId'] == child['id']:
                            child['answer'] = a['fAnswer']

                with open(os.path.join(root, file[:-5] + "-answer.json"), 'w', encoding='utf-8') as f:
                    f.write(json.dumps(json_data, indent=4, ensure_ascii=False))
