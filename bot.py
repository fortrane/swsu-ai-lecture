import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from dotenv import load_dotenv
import keyboard as kb
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sql_app.database import SessionLocal
from sql_app import models
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Потоковый пул для выполнения синхронных операций
executor = ThreadPoolExecutor()


def get_file_data(file_id: int):
    try:
        with SessionLocal() as session:
            query = select(models.FileData).where(models.FileData.file_id == file_id)
            result = session.execute(query)
            file_data = result.scalars().first()
            return file_data
    except Exception as e:
        print(f"Error fetching file data: {e}")
        return None


def save_user_id_to_db(user_id: int):
    db: Session = SessionLocal()
    try:
        existing_user = db.query(models.Logger).filter(models.Logger.telegram_id == user_id).first()
        if not existing_user:
            new_user = models.Logger(telegram_id=user_id)
            db.add(new_user)
            db.commit()
        else:
            print(f"User ID {user_id} already exists in the database.")
    except Exception as e:
        db.rollback()
        print(f"Error saving user_id to db: {e}")
    finally:
        db.close()  # Закрываем сессию


@dp.message(Command("start"))
async def first_screen(message: types.Message):
    await message.answer(text="Это бот для логов LectureAI\n Нажмите далее чтобы начать получать логи.",
                         reply_markup=kb.starting_button)


@dp.callback_query(F.data == "start_listening")
async def started_listening(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    save_user_id_to_db(user_id)
    await callback.message.edit_text(text=f"Вы слушаете логи...{user_id}")


@dp.callback_query(F.data.startswith("more_info_"))
async def more_info(callback: types.CallbackQuery):
    data = callback.data
    print(f"Callback data received: {data}")  # Логируем данные для отладки

    # Разделяем данные для получения идентификатора файла
    if "_" in data:
        parts = data.split("_", 1)
        if len(parts) == 2:
            action, file_id_str = parts
            try:
                file_id = int(file_id_str)  # Преобразование в целое число
                print(f"Extracted file ID: {file_id}")  # Логируем извлеченный идентификатор
                # Получаем данные по file_id
                loop = asyncio.get_event_loop()
                file_data = await loop.run_in_executor(
                    executor,
                    lambda: get_file_data(SessionLocal(), file_id)
                )

                if file_data:
                    qa_text_json = file_data.test
                    qa_time = file_data.qa_time
                    response_message = f"QA Text: {qa_text_json}\nExecution Time: {qa_time} seconds"
                else:
                    response_message = "Data not found."
            except ValueError:
                response_message = "Invalid file ID format."
        else:
            response_message = "Invalid callback data format."
    else:
        response_message = "Invalid callback data format."

    await callback.message.edit_text(text=response_message)


async def send_log(user_id: int, log):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Узнать больше", callback_data=f"more_info_{log['id']}")]
    ])
    await bot.send_message(chat_id=user_id, text=str(log), reply_markup=kb)


async def bot_main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(bot_main())
