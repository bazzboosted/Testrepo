import asyncio
from aiogram import Bot, Dispatcher

bot = Bot("8261198757:AAH6zT0tMVsfrud1Wq09sZ2x851jBt7tnqQ")
dp = Dispatcher()

@dp.message()
async def echo(message):
    await message.answer(message.text)

asyncio.run(dp.start_polling(bot))
