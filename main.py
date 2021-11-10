import asyncio
import re

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import markup as nav
from flow_connect import flow_connect_request, flow_get_project_list, flow_get_task_list
import aioschedule

from db import *

TOKEN = "2086025382:AAEXqSBsHoz-3jkuvECeATxMKWPyOxarDsQ"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(msg: types.Message):
    if fetchall_id(msg.from_user.id):
        await msg.answer(
            f'Здравствуйте {fetchall_fullname(msg.from_user.id)}. Вы успешно авторизованы в группе '
            f'{fetchall_group(msg.from_user.id)}\n'
            f'Чтобы узнать возможности бота вызывайте /help')
    else:
        await msg.answer(
            f'Я бот команды Enter. Приятно познакомиться, {msg.from_user.first_name}. Вам необходимо пройти этап авторизации',
            reply_markup=nav.authMenu)


@dp.message_handler(commands=['help'])
async def send_welcome(msg: types.Message):
    if fetchall_id(msg.from_user.id):
        await msg.answer(
            f'Для поставновки задач необходимо:\n'
            f'1. Выбрать исполнителя из списка пользователей. Список пользователей вызывается командой:@enter_promo_bot')
        await msg.answer_photo(photo=open('media/inline_msg_cut.jpg', 'rb'))
        await msg.answer(
            f'2. Прикрепить выбранный контакт к следущему сообщению')
        await msg.answer_photo(photo=open('media/reply_contact.jpg', 'rb'))
        await msg.answer(
            f'3. Прописать команду\nПример:\n#Задача Заголовок задачи ЦИФРА ПРОЕКТА\n')
        await msg.answer(
            f'4. Чтобы узнать список проектов, введите #Проекты')
        # await msg.answer_photo(photo=open('media/msg_end_example.png', 'rb'))
    else:
        await msg.answer(
            f'Я бот команды Enter. Приятно познакомиться, {msg.from_user.first_name}. Вам необходимо пройти этап авторизации',
            reply_markup=nav.authMenu)


@dp.message_handler()
async def send_welcome(msg: types.Message):
    print(msg.text)
    # print(msg.md_text)
    # print(msg.from_user.id)

    list_project = flow_get_project_list()
    print(type(list_project))
    print(list_project)

    if msg.text.title() == 'Авторизация':
        if fetchall_id(msg.from_user.id):
            name_group = fetchall_group(msg.from_user.id)
            if len(name_group) > 3:
                await msg.answer(
                    f'Вы авторизованы в группе {name_group}')
            else:
                await msg.answer(
                    f'Вы не состоите не в одной группе')
        else:
            await msg.answer("Необходимо связать свой аккаунт с аккаунтом из Flow\n"
                             "Введите @enter_promo_bot и выберите себя из списка.")
            await msg.answer_photo(photo=open('media/inline_msg.jpg', 'rb'))
            await msg.answer("Прикрепив контакт к сообщению введите #Name")
            await msg.answer_photo(photo=open('media/end_msg.jpg', 'rb'))

    elif '#Name' in msg.text.title():
        if not fetchall_id(msg.from_user.id):
            if not msg.values['reply_to_message']['contact']['first_name']:
                await msg.answer('Вы не прикрепили контакт человека')
            else:
                fullname = msg.values['reply_to_message']['contact']['first_name']
                if fetchall_null_id_user(fullname):
                    await msg.answer(f"Поздравляю! Вы зарегистрированы как {fullname}")
                    update_new_users(msg.from_user.id, fullname)
                    name = ''
                    if len(msg.from_user.username) > 3:
                        name = f'Никнейм в telegram:{msg.from_user.username}'
                    for boss_user in list_boss:
                        await bot.send_message(boss_user,
                                               f'Зарегистрировался новый пользователь с telegram ID "{msg.from_user.id}" прописал себе имя: "{fullname}" {name}.')
                else:
                    await msg.answer("Этот пользователь уже авторизирован")
        else:
            await msg.answer(f"Вы уже зарегистрированы в системе")

    elif '#AddGroup' in msg.text.title():
        if msg.from_user.id in list_boss:
            text = msg.text.replace('#AddGroup ', '').split(' ')
            # print(text)

            group = text[0].replace('Group:', '')
            id_user = int(text[1].replace('ID:', ''))
            if group.lower() == 'boss':
                set_value = r"boss == 'True' "
            elif group.lower() == 'moderators':
                set_value = "moderators == 'True'"
            else:
                set_value = f"other_category == '{group}' "
            update_new(set_value, id_user)
    elif '#Задача' in msg.text.title():
        if 'reply_to_message' in msg.values:
            # owner - владелец
            responsible_id_flow = msg.values['reply_to_message']['contact']['phone_number']
            responsible_id_tlg = get_tlg_id(responsible_id_flow)
            owner_id, owner_name = fetchall_flow_id(msg.from_user.id)
            title = msg.text.replace('#Задача ', '').replace('#Задача', '').replace('#задача', '').replace('#задача ',
                                                                                                           '')
            if len(title) > 3:
                project_id = re.findall(r'\d+$', title)
                if len(project_id) > 0:
                    project_name = ''
                    # list_project = flow_get_project_list()
                    for current_name in list_project:
                        if current_name['id'] == int(project_id[0]):
                            project_name = current_name['name']
                    if project_name == '':
                        await msg.answer('НЕ НАЙДЕН ИЗ СПИСКА ПРОЕКТОВ!')
                        return
                    title = title[:-3] + re.sub(project_id[0], '', title[-3:])
                    flow_connect_request(title, responsible_id_flow, owner_id, int(project_id[0]))
                    flow_id_task = flow_get_task_list(title)
                    if int(project_id[0]) == 0:
                        title_msg = title + "Без привязки к проекту "
                    else:
                        title_msg = title + "Проект: " + project_name
                    await msg.answer('Задача успешно поставлена!')
                    await bot.send_message(responsible_id_tlg, f"Вам поставлена задача от {owner_name}!\n"
                                                               f"Заголовок задачи: {title_msg} ID задачи: {flow_id_task}")
                else:
                    await msg.answer('Отсутствует номер проекта. '
                                     'Чтобы узнать номер доступных проектов напишите команду #Проекты\n'
                                     'ПРИМЕР КОМАНДЫ:\n#Задача Текст задачи ЦИФРА ПРОЕКТА')

            else:
                await msg.answer('Тело текста задачи должно быть больше 3 символов!\n ПРИМЕР:\n'
                                 '#Задача Текст задачи ЦИФРА ПРОЕКТА')
        else:
            await msg.answer('Вы не прикрепили контакт человека')

    elif '#Проекты' in msg.text.title():
        msg_list_items = ''
        if fetchall_id(msg.from_user.id):

            for items in list_project:
                id_project = items['id']
                name_project = items['name']
                msg_list_items = msg_list_items + str(id_project) + ': ' + name_project + '\n'
            await msg.answer(msg_list_items)

    elif '#Удалить' in msg.text.title():
        if 'reply_to_message' in msg.values:
            if msg.from_user.id in list_boss:
                delete_user(msg.from_user.id)
                await msg.answer('Контакт успешно удалён')
            else:
                await msg.answer('У вас нет прав для удаления!')
        else:
            await msg.answer('Вы не прикрепили контакт человека')

    else:
        await msg.answer(
            f'Команд на выпонение не найдено')


@dp.inline_handler()
async def inline_handler(query: types.InlineQuery):
    # Получение ссылок пользователя с опциональной фильтрацией (None, если текста нет)
    text = query.query
    rows = fetchall_inline_users(text)
    results = []
    id_users_list = []

    if text.title() == "Проект":
        list_project = flow_get_project_list()
        for items in list_project:
            id_project = items['id']
            name_project = items['name']
            item = types.InlineQueryResultArticle(id=id_project, title=name_project,
                                                  input_message_content=types.InputMessageContent(
                                                      message_text=id_project))
            results.append(item)
        return await query.answer(results=results, cache_time=60,
                                  is_personal=True)

    else:
        for row in rows:
            id_users_list.append(row[2])
            item = types.InlineQueryResultContact(id=f'{row[0]}', phone_number=row[0], first_name=row[1])
            results.append(item)
        # print(id_users_list)
        if query.from_user['id'] in id_users_list:
            return await query.answer(results=results, cache_time=60,
                                      is_personal=True)
        else:

            null_users = null_telegram_id_users(text)
            results_null = []
            for row_null in null_users:
                item = types.InlineQueryResultContact(id=f'{row_null[0]}', phone_number=row_null[0],
                                                      first_name=row_null[1])
                results_null.append(item)
                return await query.answer(results=results_null, cache_time=60,
                                          is_personal=True)


async def flowlu_connect_refresh():
    flow_check_users()
    global list_boss
    list_boss = fetchall_boss()


async def scheduler():
    aioschedule.every().hour.do(flowlu_connect_refresh)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
