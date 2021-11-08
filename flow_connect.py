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
        query_params.update({'model_id': model_id})

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
    id = 642
    post = rf'https://{company}.flowlu.ru/api/v1/module/task/tasks/get/{id}?api_key={api_key}'
    # query_params.update(
    #     {'name': f'{title}', 'description': 'Задача создана посредством работы бота в телеграмме',
    #      'priority': 1, 'responsible_id': responsible_id, 'owner_id': owner_id, 'type': 0})

    print(query_params)
    new_post = requests.get(post)
    print(new_post)
    print(new_post.text)


def flow_get_project_list() -> list:
    # query_params = {"api_key": api_key}
    post = rf'https://{company}.flowlu.ru/api/v1/module/st/projects/list?api_key={api_key}'
    # print(query_params)
    new_post = requests.get(post)
    # print(new_post)
    # print(new_post.text)
    js_text = json.loads(new_post.text)
    result = [{'id': 0, 'name': 'Без названия'}]
    for row in js_text['response']['items']:
        result.append(row)
    # print()
    return result


# flow_delete()
# flow_get_project_list()
# flow_get()
