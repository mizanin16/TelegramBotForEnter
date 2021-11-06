from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


# --- Авторизация ---
btnAuth = KeyboardButton('Авторизация')
authMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnAuth)
