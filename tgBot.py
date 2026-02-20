import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

bot = Bot("8261198757:AAH6zT0tMVsfrud1Wq09sZ2x851jBt7tnqQ")
dp = Dispatcher()

class States(StatesGroup):
    name = State()
    choosingDish = State()
    
@dp.message(F.text == "/start")
async def FirstAnswer(msg, state:FSMContext):
    await msg.answer("Назовите имя")
    await state.set_state(States.name)

@dp.message(States.name)
async def FirstMsg(msg, state: FSMContext):
    await msg.answer("Выберите рецепт продукта, " + msg.text)
    await state.update_data(name = msg.text)
    await state.set_state(States.choosingDish)

@dp.message(States.choosingDish)
async def Receipts(receipt, state: FSMContext):
    dish = receipt.text
    if (dish == "чай"):
        await receipt.answer("кинуть пакетик в кружку")
    if (dish == "суп"):
        await receipt.answer("вода картошка кобаса морковь")
    else:
        await receipt.answer("введите суп или чай")

    
    
    
    
    

asyncio.run(dp.start_polling(bot))
