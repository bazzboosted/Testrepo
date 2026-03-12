import asyncio
import json
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import sqlite3
import os


script_dir = os.path.dirname(os.path.abspath(__file__))
receipts_path = os.path.join(script_dir, "receipts.json")

with open(receipts_path, "r", encoding="utf-8") as f:
    recipes = json.load(f)

path = r"C:\Git\Project\botDatabase"
conn = sqlite3.connect(path)
cursor = conn.cursor()

cursor.execute("select * from dishes")
rows = cursor.fetchall()
for row in rows:
    print(row)

bot = Bot("8261198757:AAH6zT0tMVsfrud1Wq09sZ2x851jBt7tnqQ")
dp = Dispatcher()
name = ""

def GetKeyboard():
    keyboard = ReplyKeyboardMarkup(keyboard=
        [
            [KeyboardButton(text = "чай"), KeyboardButton(text = "суп"),
             KeyboardButton(text = "тушенка совок"), KeyboardButton(text = "лазанья"),
             KeyboardButton(text = "компот"),
             KeyboardButton(text = "Избранное")
             ]
            ])
    resize_keyboard = True
    one_time_keyboard = True
    return keyboard

class States(StatesGroup):
    nameState = State()
    choosingDishState = State()
    afterChoosingState = State()
  
@dp.message(F.text == "/start")
async def FirstAnswer(msg, state: FSMContext):
    await msg.answer("назовите ваше имя")
    await state.set_state(States.nameState)

@dp.message(F.text == "Избранное")
async def CheckFavorite(msg, state: FSMContext):
    cursor.execute("SELECT dish FROM favorites WHERE tgId = ?", (msg.from_user.id,))
    rows = cursor.fetchall()
    if rows:
        text = "Ваше избранное:\n" + "\n".join(row[0] for row in rows)
    else:
        text = "У вас пока нет избранных блюд"
    await msg.answer(text)

@dp.message(States.nameState)
async def FirstMsg(msg, state: FSMContext):
    await msg.answer("Выберите рецепт продукта, " + msg.text, reply_markup=GetKeyboard())
    name = msg.text
    cursor.execute(
        "insert or ignore INTO users (tgId, name) values (?, ?)",
        (msg.from_user.id, name)
    )
    conn.commit()
    await state.set_state(States.choosingDishState)

@dp.message(States.choosingDishState) 
async def Receipts(msg, state: FSMContext):
    dish = msg.text
    if (dish in recipes):
        cursor.execute("SELECT name FROM users WHERE tgId = ?", (msg.from_user.id,))
        row = cursor.fetchone()
        name = row[0]
        await state.update_data(current_dish=dish) 
        inline_kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=" Добавить в избранное", callback_data="add"),
                InlineKeyboardButton(text=" Нет", callback_data="skip")
            ]
        ])
        await msg.answer(recipes[dish])
        await msg.answer("Вам понравилось, " + name + "? Хотите добавить в избранное?", reply_markup=inline_kb)
    else:
        await msg.answer("выберите то, что на кнопках")

@dp.callback_query(F.data == "add")
async def OnAddFavorite(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    dish = data.get("current_dish")
    AddFavorite(callback.from_user.id, dish)
    await callback.message.edit_text(dish + " добавлено в избранное")

@dp.callback_query(F.data == "skip")
async def OnSkipFavorite(callback: CallbackQuery):
    await callback.answer()

def AddFavorite(tgId: int, dish: str):
    cursor.execute(
        "INSERT OR IGNORE INTO favorites (tgId, dish) VALUES (?, ?)",
        (tgId, dish)
    )
    conn.commit()
        


asyncio.run(dp.start_polling(bot))
