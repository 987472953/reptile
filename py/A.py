import json

data = json.load(open("../downloadExercise/data.json", encoding='utf-8'))
print(data)
print(data['id'])
print(data['parentId'])
print(data['title'])
print(data['version'])
questions_ = data['questions']
print(questions_)
print("---------------------")
print("---------------------")
print("---------------------")

for q in questions_:
    # print(q)
    id_ = q['id']
    parent_id_ = q['parentId']
    title_ = q['title']
    # print(id_)
    # print(parent_id_)
    # print(title_)
    q_questions_ = q['questions']
    owner_data = {}
    owner_data['id'] = id_
    owner_data['parent_id'] = parent_id_
    owner_data['title'] = title_
    inner_data = []
    owner_data['inner_data'] = inner_data
    for inner_q in q_questions_:
        if inner_q['id'] != id_:
            print("id不相同")
        if inner_q['parentId'] != parent_id_:
            print("id不相同")
        if inner_q['title'] != title_:
            print("title不相同")

        for innerinner_q in inner_q['questions']:
            inner_data_q = {}
            inner_data_q["id"] = innerinner_q['id']
            inner_data_q["parentId"] = innerinner_q['parentId']
            inner_data_q["title"] = innerinner_q['title']
            inner_data_q_q = []
            inner_data_q["q"] = inner_data_q_q
            inner_data.append(inner_data_q)
            # print("inner inner ", innerinner_q['parentId'])
            # print("inner inner ", innerinner_q['id'])
            # print("inner inner ", innerinner_q['title'])
            for answerFlow in innerinner_q['answerFlow']:
                for answerFlows in answerFlow:
                    # print(answerFlows['name'])
                    # print(answerFlows['order'])
                    # print(answerFlows['value'])
                    inner_data_q_q.append(answerFlows['value'])
                    # print(answerFlows['valueType'])
                    # print('')

    print(owner_data)