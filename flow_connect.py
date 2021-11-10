import json

import requests

company = 'enterpromo'
api_key = 'YnI0WDFIZ1hlSTMwUGNkU1E1MThSZnI4cXJxeFBHczNfNzMxMzQ'


def flow_connect_request(title: str, responsible_id: int, owner_id: int, model_id: int):
    query_params = {"api_key": api_key}
    post = rf'https://{company}.flowlu.ru/api/v1/module/task/tasks/create'
    query_params.update(
        {'name': f'{title}', 'description': 'Задача создана посредством работы бота в телеграмме',
         'priority': 1, 'responsible_id': responsible_id, 'owner_id': owner_id, 'type': 0})
    if model_id != 0:
        query_params.update({"module": "st", "model": "project", 'model_id': model_id, 'project_stage_id': 1})
    # print('flow_connect_request success')
    print(query_params)
    new_post = requests.post(post, data=query_params)
    print(new_post)
    print(new_post.text)


def flow_delete():
    query_params = {"api_key": api_key}
    id = 678
    post = rf'https://{company}.flowlu.ru/api/v1/module/task/tasks/delete/{id}'
    # query_params.update(
    #     {'name': f'{title}', 'description': 'Задача создана посредством работы бота в телеграмме',
    #      'priority': 1, 'responsible_id': responsible_id, 'owner_id': owner_id, 'type': 0})

    print(query_params)
    new_post = requests.post(post, data=query_params)
    print(new_post)
    print(new_post.text)


def flow_get():
    query_params = {"api_key": api_key}
    id = 478
    post = rf'https://{company}.flowlu.ru/api/v1/module/task/tasks/list?api_key={api_key}'
    # post = rf'https://{company}.flowlu.ru/api/v1/module/task/tasks/get/{id}?api_key={api_key}'
    # query_params.update(
    #     {'name': f'{title}', 'description': 'Задача создана посредством работы бота в телеграмме',
    #      'priority': 1, 'responsible_id': responsible_id, 'owner_id': owner_id, 'type': 0})
    query_params_new = []
    print(query_params)
    new_post = requests.get(post)
    print(new_post)
    print(new_post.text)
    js_text = json.loads(new_post.text)
    print(js_text)
    # print(js_text['response']['workflow_id'])
    # print(js_text['response']['workflow_stage_id'])
    print()


def flow_get_task_list(name) -> int:
    # print(name)
    post = rf'https://{company}.flowlu.ru/api/v1/module/task/tasks/list?api_key={api_key}'
    new_post = requests.get(post)
    js_text = json.loads(new_post.text)
    # print(js_text)
    for row in js_text['response']['items']:
        if name == row['name']:
            return int(row['id'])


def flow_get_project_list() -> list:
    # query_params = {"api_key": api_key}
    post = rf'https://{company}.flowlu.ru/api/v1/module/st/projects/list?api_key={api_key}'
    # print(query_params)
    new_post = requests.get(post)
    # print(new_post)
    # print(new_post.text)
    js_text = json.loads(new_post.text)
    result = [{'id': 0, 'name': 'Без проекта'}]
    for row in js_text['response']['items']:
        result.append({'id': row['id'], 'name': row['name']})
    return result


def flow_update_task(id_task):
    query_params = {"api_key": api_key}
    post = rf'https://{company}.flowlu.ru/api/v1/module/task/tasks/update/{id}'
    # print(query_params)
    query_params.update({'workflow_stage_id': id_task})
    new_post = requests.post(post, data=query_params)
    print(new_post)
    # 1/4 завершено 1/1 сделать 1/2 в работе 1/3 сделано


# flow_delete()
# flow_get_project_list()
# flow_get()
# flow_get_task_list()
