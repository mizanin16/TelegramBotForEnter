import requests

company = 'enterpromo'
api_key = 'YnI0WDFIZ1hlSTMwUGNkU1E1MThSZnI4cXJxeFBHczNfNzMxMzQ'


def flow_connect_request(title: str, responsible_id: int, owner_id: int):
    query_params = {"api_key": api_key}
    post = rf'https://{company}.flowlu.ru/api/v1/module/task/tasks/create'
    query_params.update(
        {'name': f'{title}', 'description': 'Задача создана посредством работы бота в телеграмме',
         'priority': 1, 'responsible_id': responsible_id, 'owner_id': owner_id, 'type': 0})

    print(query_params)
    new_post = requests.post(post, data=query_params)
    print(new_post)
    print(new_post.text)


def flow_delete():
    query_params = {"api_key": api_key}
    id = 671
    post = rf'https://{company}.flowlu.ru/api/v1/module/task/tasks/delete/{id}'
    # query_params.update(
    #     {'name': f'{title}', 'description': 'Задача создана посредством работы бота в телеграмме',
    #      'priority': 1, 'responsible_id': responsible_id, 'owner_id': owner_id, 'type': 0})

    print(query_params)
    new_post = requests.post(post, data=query_params)
    print(new_post)
    print(new_post.text)


flow_delete()
