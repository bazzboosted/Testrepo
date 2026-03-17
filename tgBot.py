import asyncio
import json
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()


script_dir = os.path.dirname(os.path.abspath(__file__))
receipts_path = os.path.join(script_dir, "receipts.json")
dbPath = os.path.join(script_dir, "botDatabase")

with open(receipts_path, "r", encoding="utf-8") as f:
    recipes = json.load(f)


conn = sqlite3.connect(dbPath)
cursor = conn.cursor()

cursor.execute("select * from dishes")
rows = cursor.fetchall()
for row in rows:
    print(row)

token = os.getenv("BOT_TOKEN")
bot = Bot(token)
dp = Dispatcher()

def InitDb():
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS "users" (
            tgId INTEGER NOT NULL,
            name TEXT,
            CONSTRAINT User_PK PRIMARY KEY (tgId)
        );

        CREATE TABLE IF NOT EXISTS dishes (
            name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            time TEXT,
            CONSTRAINT dishes_pk PRIMARY KEY (name)
        );

        CREATE TABLE IF NOT EXISTS favorites (
            tgId INTEGER,
            dish TEXT,
            CONSTRAINT favorites_dishes_FK FOREIGN KEY (dish) REFERENCES dishes(name) ON DELETE SET NULL,
            CONSTRAINT favorites_User_FK FOREIGN KEY (tgId) REFERENCES "users"(tgId) ON DELETE SET NULL
        );
    """)
    conn.commit() //'это взято из dbeaver полностью'
    
    
def GetKeyboard():
    cursor.execute("select name from dishes")
    rows = cursor.fetchall()
    buts = [KeyboardButton(text=row[0]) for row in rows]
    keyboard = ReplyKeyboardMarkup(
        keyboard=[buts, [KeyboardButton(text="Избранное")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

class States(StatesGroup):
    WaitForName = State()
    ChoosingDish = State()
    AfterChoosingDish = State()
  
@dp.message(F.text == "/start")
async def FirstAnswer(msg, state: FSMContext):
    InitDb()
    await msg.answer("назовите ваше имя")
    await state.set_state(States.WaitForName)

@dp.message(F.text == "Избранное")
async def CheckFavorite(msg, state: FSMContext):
    cursor.execute("SELECT dish FROM favorites WHERE tgId = ?", (msg.from_user.id,))
    rows = cursor.fetchall()
    if rows:
        text = "Ваше избранное:\n" + "\n".join(row[0] for row in rows)
    else:
        text = "У вас пока нет избранных блюд"
    await msg.answer(text)

@dp.message(States.WaitForName)
async def FirstMsg(msg, state: FSMContext):
    await msg.answer("Выберите рецепт продукта, " + msg.text, reply_markup=GetKeyboard())
    name = msg.text
    cursor.execute(
        "insert or ignore INTO users (tgId, name) values (?, ?)",
        (msg.from_user.id, name)
    )
    conn.commit()
    await state.set_state(States.ChoosingDish)

@dp.message(States.ChoosingDish) 
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
