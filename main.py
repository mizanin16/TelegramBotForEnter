import asyncio
import re
import aioschedule

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

import markup as nav
from config import TELEGRAM_API_TOKEN
from flow_connect import *

from db import *

TOKEN = TELEGRAM_API_TOKEN
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
media_dir = os.path.join(BASE_DIR, 'media')


@dp.message_handler(commands=['start'])
async def send_welcome(msg: types.Message):
    """
    Ответ на сообщение /start
    """
    if fetchall_id(msg.from_user.id):
        # Если пользователь добавлен в список пользователей в БД
        await msg.answer(
            f'Здравствуйте {fetchall_fullname(msg.from_user.id)}. Вы успешно авторизованы в группе '
            f'{fetchall_group(msg.from_user.id)}\n'
            f'Чтобы узнать возможности бота вызывайте /help')
    else:
        # Если пользователь не зарегистрирован, предлагается зарегистрироваться из списка, который получаем из flow
        await msg.answer(
            f'Я бот команды Enter. Приятно познакомиться, {msg.from_user.first_name}. '
            f'Вам необходимо пройти этап авторизации',
            reply_markup=nav.authMenu)


@dp.message_handler(commands=['help'])
async def send_welcome(msg: types.Message):
    """
    Ответ на сообщение /help
    """
    if fetchall_id(msg.from_user.id):
        # Если пользователь добавлен в список пользователей в БД, Бот отправляет порядок действий
        await msg.answer(
            f'Для поставновки задач необходимо:\n'
            f'1. Выбрать исполнителя из списка пользователей. Список пользователей вызывается командой:@enter_promo_bot')
        await msg.answer_photo(photo=open(os.path.join(media_dir, 'inline_msg_cut.jpg'), 'rb'))
        await msg.answer(
            f'2. Прикрепить выбранный контакт к следущему сообщению')
        await msg.answer_photo(photo=open(os.path.join(media_dir, 'reply_contact.jpg'), 'rb'))
        await msg.answer(
            f'3. Прописать команду\nПример:\n#Задача Заголовок задачи ЦИФРА ПРОЕКТА\n')
        await msg.answer(
            f'4. Чтобы узнать список проектов, введите #Проекты')
        await msg.answer(
            f'5. Чтобы изменить этап проекта, необходимо прикрепить сообщение с поставленной задачей и ввести команду\n'
            f'Список доступных команд:\n #Сделать \n #В Работе \n #Сделано \n #Завершено')
    else:
        # Если пользователь не зарегистрирован, предлагается зарегистрироваться из списка, который получаем из flow
        await msg.answer(
            f'Я бот команды Enter. Приятно познакомиться, {msg.from_user.first_name}. Вам необходимо пройти этап авторизации',
            reply_markup=nav.authMenu)


@dp.message_handler()
async def send_welcome(msg: types.Message):
    """
    Получаем сообщение Боту и производим соотношение команд
    """
    print('Message = ' + msg.text)

    list_project = flow_get_project_list()
    dict_stage_workflow = {'#сделать': 1, '#в работе': 2, '#вработе': 2, '#в_работе': 2, '#сделано': 3, '#завершено': 4}
    if msg.text.title() == 'Авторизация':
        # Проверяем авторизацию пользователя
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
            await msg.answer_photo(photo=open(os.path.join(media_dir, 'inline_msg.jpg'), 'rb'))
            await msg.answer("Прикрепив контакт к сообщению введите #Name")
            await msg.answer_photo(photo=open(os.path.join(media_dir, 'end_msg.jpg'), 'rb'))

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
        # Добавляем в группу пользователя
        if msg.from_user.id in list_boss:
            text = msg.text.replace('#AddGroup ', '').split(' ')
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
        # Ставим задачу пользователю
        if 'reply_to_message' in msg.values:
            responsible_id_flow = msg.values['reply_to_message']['contact']['phone_number']
            responsible_id_tlg = get_tlg_id(flow_id=responsible_id_flow, flow_name=None)
            owner_id, owner_name = fetchall_flow_id(msg.from_user.id)
            title = msg.text
            title = title.replace('#Задача ', '').replace('#Задача', '').replace('#задача ', '').replace('#задача', '')
            if len(title) > 3:
                project_id = re.findall(r'\d+$', title)
                if len(project_id) > 0:
                    project_name = ''
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
                    await msg.answer(f'Задача успешно поставлена! \nID задачи: {flow_id_task}')
                    await bot.send_message(responsible_id_tlg, f"Вам поставлена задача от {owner_name}!\n"
                                                               f"Заголовок задачи: {title_msg} \nID задачи: {flow_id_task}")
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
        # Получаем список проектов
        msg_list_items = ''
        if fetchall_id(msg.from_user.id):

            for items in list_project:
                id_project = items['id']
                name_project = items['name']
                msg_list_items = msg_list_items + str(id_project) + ': ' + name_project + '\n'
            await msg.answer(msg_list_items)

    elif '#Удалить' in msg.text.title():
        # Удаляем поставленную задачу
        if 'reply_to_message' in msg.values:
            if msg.values['reply_to_message']['contact']:
                if msg.from_user.id in list_boss:
                    user = msg.values['reply_to_message']['contact']['first_name']
                    delete_user(user)
                    await msg.answer('Контакт успешно удалён')
                else:
                    await msg.answer('У вас нет прав для удаления!')
                return
            elif 'ID задачи:' in msg.values['reply_to_message']['text']:
                text = msg.values['reply_to_message']['text']
                id_tlg = text[text.find('ID задачи:') + 11:]
                id_tlg = id_tlg[:id_tlg.find('\n')]
                if flow_delete(id_tlg):
                    await msg.answer('Задача успешно удалена!')
                else:
                    await msg.answer('Ошибка при удалении!')
            else:
                await msg.answer('Сообщение не корректно отправлено!')
        else:
            await msg.answer('Сообщение не прикреплено!')
    elif msg.text.lower() in dict_stage_workflow.keys():
        # Изменение этапа разработки
        if 'reply_to_message' in msg.values:
            if 'ID задачи:' in msg.values['reply_to_message']["text"]:
                stage = msg.text.title().replace("#", "")
                text_msg = msg.values['reply_to_message']['text']
                id_tlg = text_msg[text_msg.find('ID задачи:') + 11:]
                if text_msg.find('от') == -1:
                    await msg.answer(f"Сообщение прикреплено не корректно!!")
                    return
                owner_name = text_msg[text_msg.find('от') + 3:text_msg.find('!\n')]
                print(id_tlg)
                if not id_tlg.isdigit():
                    await msg.answer(f"Задача выбрана некорректно!")
                else:
                    flow_update_task(id_tlg, stage=dict_stage_workflow[msg.text.lower()])
                    await msg.answer(f"Успешно произведено изменение этапа проекта.\nЭтап: {stage}")
                    owner_id_tlg = get_tlg_id(flow_id=None, flow_name=owner_name)
                    responsible_id, responsible_name = fetchall_flow_id(msg.from_user.id)
                    msg_answer_to_owner = f'{text_msg[text_msg.find("Заголовок задачи"):]}\n' \
                                          f'Пользователь {responsible_name} изменил этап задачи проекта.\nЭтап: {stage}'

                    await bot.send_message(owner_id_tlg, msg_answer_to_owner)

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
    """
    Определениен списка пользователей и обновление списка пользователей
    :return:
    """
    flow_check_users()
    global list_boss
    list_boss = fetchall_boss()


async def scheduler():
    """
    Настройка выполнения асинхронной функции
    :return:
    """
    aioschedule.every().hour.do(flowlu_connect_refresh)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    """
    Создание асинхронной функции раз в час для опроса БД
    """
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
