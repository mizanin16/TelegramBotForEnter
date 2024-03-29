import os
import sqlite3
from datetime import datetime
import json
import requests
from config import NAME_COMPANY_FLOW, API_COMPANY_FLOW

conn = sqlite3.connect(os.path.join("db", "users.db"))
cursor = conn.cursor()

company = NAME_COMPANY_FLOW
api_key = API_COMPANY_FLOW


def update_new(set_values: str, where_values: int):
    cursor.execute(
        f"UPDATE users "
        f"SET {set_values} "
        f"WHERE {where_values}")
    conn.commit()


def update_new_users(id_tlg: int, fullname: str):
    cursor.execute(
        f"UPDATE users "
        f"SET created = '{datetime.now().isoformat()}', "
        f"id_user = '{id_tlg}' "
        f"WHERE flow_name = '{fullname}' and id_user")
    conn.commit()


def fetchall_fullname(id_users: str) -> str:
    cursor.execute(f"SELECT flow_name FROM users where id_user ='{id_users}'")
    row = cursor.fetchone()
    if row:
        return row[0]


def fetchall_id(id_users: str) -> bool:
    cursor.execute(f"SELECT id_user FROM users where id_user ='{id_users}' ")
    row = cursor.fetchone()
    if row:
        return True
    else:
        return False


def fetchall_null_id_user(fullname: str) -> bool:
    cursor.execute(f"SELECT * FROM users where flow_name ='{fullname}' and id_user is Null ")
    row = cursor.fetchone()
    if row:
        return True
    else:
        return False


def fetchall_flow_id(id_users: int) -> list:
    cursor.execute(f"SELECT flow_id, flow_name FROM users where id_user ='{id_users}' ")
    row = cursor.fetchone()
    if row:
        return row


def delete_user(flow_name: str):
    cursor.execute(f"DELETE FROM users WHERE flow_name = '{flow_name}' ")
    conn.commit()


def fetchall_inline_users(text) -> list:
    if text != '':
        text = f"WHERE flow_name LIKE '%{text.title()}%' "
    cursor.execute(f"SELECT flow_id, flow_name, id_user  FROM users {text} order by flow_name")
    rows = cursor.fetchall()
    return rows


def get_tlg_id(flow_id: str or None, flow_name: str or None) -> str:
    if not flow_id:
        where = f'flow_name = "{flow_name}" '
    else:
        where = f'flow_id = "{flow_id}" '
    cursor.execute(f"SELECT id_user FROM users where {where} ")
    row = cursor.fetchone()
    return row[0]


def null_telegram_id_users(text) -> list:
    if text != '':
        text = f" and flow_name LIKE '%{text.title()}%' "
    cursor.execute(f"SELECT flow_id, flow_name FROM users WHERE id_user is Null {text} order by flow_name")
    rows = cursor.fetchall()
    return rows


def fetchall_boss() -> list:
    cursor.execute(f"SELECT id_user FROM users where BOSS == 'True'")
    row = cursor.fetchall()
    if row:
        return row[0]


def fetchall_group(id_users: str) -> str:
    cursor.execute(f"SELECT boss, moderators, other_category FROM users where id_user ='{id_users}'")
    rows = cursor.fetchone()
    if rows[0] or rows[1] or rows != '':
        out_text = ''
        if rows[0] is not None:
            out_text = out_text + 'BOSS'
        if rows[1]:
            out_text = out_text + ' Moderators'
        if rows[2] is not None:
            out_text = out_text + ' Other_category=' + rows[2]
        return out_text
    else:
        return ''


def flow_check_users():
    """
    Заполнение списка пользователей из флоулу
    """
    conn = sqlite3.connect(os.path.join("db", "users.db"))
    cursor = conn.cursor()
    get_users = fr'https://{company}.flowlu.ru/api/v1/module/core/user/list?api_key={api_key}'
    sd = requests.get(get_users)
    # print(sd)
    # print(sd.text)
    all_users = sd.text
    # print()
    js_text = json.loads(all_users)
    for user in js_text['response']['items']:
        info_users = user['name'], user['id'], user['username']
        try:
            cursor.execute(
                f"INSERT or IGNORE INTO users "
                f"(flow_name, flow_id, flow_email) "
                f"VALUES {info_users}")
        except Exception as ex:
            print(ex)
    conn.commit()
