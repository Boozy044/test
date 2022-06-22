from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, ContentType
from databases import Database
import logging
import config

logging.basicConfig(level=logging.INFO)

database = Database(f'mysql+aiomysql://{config.USER}:{config.PASSWORD}@{config.HOST}/{config.DATABASE}')
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)


def get_full_name(message):
    return str(message.chat.first_name) + " " + str(message.chat.last_name)


async def get_answer(question):
    await database.connect()

    query = f"SELECT t2.`corrective`, t2.`answer` FROM `questions` t1 LEFT JOIN `questions` t2 ON t1.`corrective` = t2.`corrective` WHERE t1.`question` = ( '{question}' ) LIMIT 1"
    result = await database.fetch_one(query=query)

    await database.disconnect()

    return result


async def make_logs(id, full_name, question, corrective, answer):
    await database.connect()

    query = f"INSERT INTO `logs`(`channel`, `user_id`, `full_name`, `question`, `corrective`, `answer`) VALUES ('Telegram', '{id}', '{full_name}', '{question}', '{corrective}', '{answer}')"
    await database.execute(query=query)

    await database.disconnect()


@dp.message_handler(content_types=[ContentType.TEXT])
async def user_answer(message: Message):
    full_name = get_full_name(message)

    answer = await get_answer(message.text)

    print(answer)

    if answer:
        if message.text == "/start":
            await message.answer(f"{answer[1]}")
        else:
            await message.answer(f"{answer[1]}")

        await make_logs(message.chat.id, full_name, message.text, answer[0], answer[1])

    else:
        answer = await get_answer("NOT_FOUND")
        await message.answer(f"{answer[1]}")
        await make_logs(message.chat.id, full_name, message.text, answer[0], answer[1])


@dp.message_handler(content_types=[ContentType.VOICE])
async def voice_message_handler(message: Message):
    full_name = get_full_name(message)

    answer = await get_answer("VOICE")
    await message.answer(f"{answer[1]}")
    await make_logs(message.chat.id, full_name, message.text, answer[0], answer[1])


@dp.message_handler(content_types=[ContentType.PHOTO])
async def photo_message_handler(message: Message):
    full_name = get_full_name(message)

    answer = await get_answer("PHOTO")
    await message.answer(f"{answer[1]}")
    await make_logs(message.chat.id, full_name, message.text, answer[0], answer[1])


@dp.message_handler(content_types=[ContentType.VIDEO])
async def video_message_handler(message: Message):
    full_name = get_full_name(message)

    answer = await get_answer("VIDEO")
    await message.answer(f"{answer[1]}")
    await make_logs(message.chat.id, full_name, message.text, answer[0], answer[1])


@dp.message_handler(content_types=[ContentType.DOCUMENT])
async def document_message_handler(message: Message):
    full_name = get_full_name(message)

    answer = await get_answer("DOCUMENT")
    await message.answer(f"{answer[1]}")
    await make_logs(message.chat.id, full_name, message.text, answer[0], answer[1])


if __name__ == '__main__':
  executor.start_polling(dp, skip_updates=True)
