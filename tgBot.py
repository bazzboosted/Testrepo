import asyncio
from aiogram import Bot, Dispatcher, F

bot = Bot("8261198757:AAH6zT0tMVsfrud1Wq09sZ2x851jBt7tnqQ")
dp = Dispatcher()

@dp.message(F.text == "Привет")
async def hello(msg):
    await msg.answer("привет")

@dp.message()
async def echo(msg):
    await msg.answer(msg.text)


asyncio.run(dp.start_polling(bot))
