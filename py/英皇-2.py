import json
import re
import string

from bs4 import BeautifulSoup

questions = []
exam = 5
# success_str = "正确答案"
success_str = "Correct Answer"

abc = string.ascii_uppercase


def get_answer_tags(search):
    """
    拿到所有答案的标签
    :param search:
    :return:
    """
    while True:
        search = search.findNextSibling()
        if tag.name == 'p':
            break
        if search.find_all("p"):
            break
    result = []
    while True:
        if search.name != 'p' and not search.find_all("p"):
            break
        result.append(search)
        search = search.findNextSibling()
    return result


def clear_soup(soup_):
    for p in soup_.find_all('p'):
        p.replaceWithChildren()
    for br in soup_.find_all('br'):
        br.replace_with("\n")
    for br in soup_.find_all('strong'):
        br.replaceWithChildren()
    for br in soup_.find_all('span'):
        br.replaceWithChildren()
    for br in soup_.find_all('em'):
        br.replaceWithChildren()


if __name__ == '__main__':
    with open("yinghuang/{}/{}.json".format(str(exam), str(exam)), "r") as json_file:
        read = json_file.read()
        json_dict = json.loads(read)

    for key, value in json_dict.items():
        soup = BeautifulSoup(value, 'html.parser')
        outer = soup.find('div', id='qtext-outer')

        question = {}
        qtextp = outer.find_all(['p', 'img'])
        alternatives = outer.find('div', id='alternatives')

        if alternatives:
            exclude_tags = alternatives.find_all(['p', 'img'])
            qtextp = [x for x in qtextp if x not in exclude_tags]

        q_t = ""
        img_index = 1
        question_img_set = set()
        for tag in qtextp:
            soup = BeautifulSoup(str(tag), 'html.parser')
            img_tags = soup.find_all('img')
            for img_tag in img_tags:
                if question_img_set.__contains__(img_tag['src']):
                    img_tag.replaceWithChildren()
                    continue
                question_img_set.add(img_tag['src'])
                url = "image/" + key + "_" + str(img_index) + ".png"
                img_index += 1
                img_tag['src'] = url
            clear_soup(soup)
            q_t += str(soup)

        question["question"] = q_t

        alternatives = outer.find('div', id='alternatives')
        qtextp = alternatives.find_all('p')
        print("result")
        q_r = ""
        for p_tag in qtextp:
            have_img = False
            # 拿到标签里面的子标签
            soup = BeautifulSoup(str(p_tag), 'html.parser')
            img_tags = soup.find_all('img')
            for img_tag in img_tags:
                url = "image/" + key + "_" + str(img_index) + ".png"
                img_index += 1
                img_tag['src'] = url
            clear_soup(soup)
            q_r += str(soup)

            if not have_img:
                q_r += "\n"
        print(q_r)
        items = []
        question["items"] = items
        for option in q_r.split("\n"):
            if option == "":
                continue
            type = "image" if "<img" in option else "text"
            items.append({type: option})
        print()
        print()
        questions.append(question)

    with open("yinghuang/{}/{}".format(str(exam), str(exam) + ".html"), "r") as answer_file:
        file_read = answer_file.read()
        soup = BeautifulSoup(file_read, 'html.parser')


        def has_specific_text(tag):
            return tag.name == 'tr' and 'feedback-qtext' in tag.text


        def has_ansower_text(tag):
            return tag.name == 'th' and success_str in tag.text


        matching_tr_tags = soup.find_all(has_ansower_text)
        q = 1
        for matching_tr_tag in matching_tr_tags:
            answer_tags = get_answer_tags(matching_tr_tag.parent)
            print(answer_tags)
            r_answer = set()
            for a in answer_tags:
                ansower_p = a.find_all("p")
                for ap in ansower_p:
                    if ap.find_all("p"):
                        continue
                    if ap.text == "未回答":
                        continue
                    ansower_str = ap.text
                    if "$IMAGE" in ansower_str:
                        match = re.search(r"alt='(.*?)'", ansower_str)
                        if not match:
                            r_answer.add(ansower_str)
                            continue
                        for qi in questions[q - 1]["items"]:
                            if match.group(1) in qi["image"]:
                                ansower_str = qi["image"]
                                break
                    r_answer.add(ansower_str)

            r_answer = list(r_answer)
            valid_answers = []
            for r in r_answer:
                if r != "" and r != "Unanswered":
                    valid_answers.append(r)

            if len(valid_answers) == 1:
                valid_answers = valid_answers[0]
                questions[q - 1]["type"] = "[ 单选 ] "
            else:
                questions[q - 1]["type"] = "[ 多选 ] "
            questions[q - 1]["answer"] = valid_answers
            q += 1
        for question in questions:
            # 遍历选项与答案
            if len(question["items"]) == 0:
                question["type"] = "[ 未知 ] "
                continue
            if '<img' in question['answer'] and question["answer"].startswith("<img") and question["answer"].endswith(
                    ">"):
                img_tag = BeautifulSoup(question["answer"], 'html.parser')
                src = img_tag.find("img").get('src')
                question["answer"] = src

            for item in question['items']:
                if "image" in item:
                    # 不以<img 开头
                    if not item["image"].startswith("<img") and not item["image"].endswith(">"):
                        # 修改key为text
                        item["text"] = item.pop("image")
                        split_text = re.split(r'\$IMAGE\[[^\]]+\]', question["answer"])
                        yes = True
                        for s in split_text:
                            if s not in item["text"]:
                                yes = False
                        if yes:
                            question["answer"] = abc[question["items"].index(item)]
                        continue

                    img_tag = BeautifulSoup(item["image"], 'html.parser')
                    src = img_tag.find("img").get('src')
                    item["image"] = src
                    if question["answer"] == item["image"]:
                        question["answer"] = abc[question["items"].index(item)]
                if "text" in item:
                    if question["answer"] == item["text"]:
                        question["answer"] = abc[question["items"].index(item)]

    print(json.dumps(questions, indent=4, ensure_ascii=False))
    # # 写入到文件
    with open("yinghuang/{}/{}.json".format(str(exam), "data"), "w") as json_file:
        json_file.write(json.dumps(questions, indent=4, ensure_ascii=False))
