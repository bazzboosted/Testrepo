
import asyncio
import json
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import sqlite3
import os


script_dir    = os.path.dirname(os.path.abspath(__file__))
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

@dp.message(States.nameState)
async def FirstMsg(msg, state: FSMContext):
    await msg.answer("Выберите рецепт продукта, " + msg.text, reply_markup=GetKeyboard())
    name=msg.text
    await state.set_state(States.choosingDishState)

@dp.message(States.choosingDishState) 
async def Receipts(msg, state: FSMContext):
    dish = msg.text
    if (dish in recipes):
        await msg.answer(recipes[dish])
        await msg.answer("вам понравилось?" + name)
        await state.set_state(States.afterChoosingState)
    else:
        await msg.answer("выберите то, что на кнопках")
    
    
    

    


asyncio.run(dp.start_polling(bot))
