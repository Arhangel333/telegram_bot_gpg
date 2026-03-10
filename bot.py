import os
import subprocess
import asyncio
from pathlib import Path
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен вашего бота
BOT_TOKEN = "8727876522:AAG1NBxqX6zGcNPy9FTzaiDoxfuELPQL6X0"
my_file_name = "max_key.asc"
TEMP_DIR = "temp_gpg_files"
CONST_DIR = "const_gpg_files"

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Директория для временных файлов
os.makedirs(TEMP_DIR, exist_ok=True)

# Директория для невременных файлов
os.makedirs(CONST_DIR, exist_ok=True)

# Команда старт
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я бот для работы с GPG файлами.\n"
        "Просто отправь мне файл с расширением .asc, "
        "и я обработаю его с помощью GPG и верну результат."
    )

# Обработчик документов
@dp.message(F.document)
async def handle_document(message: Message):
    try:
        document = message.document
        file_name = document.file_name
        
        # Проверяем расширение файла
        if not file_name.endswith('.asc'):
            await message.answer("❌ Пожалуйста, отправьте файл с расширением .asc")
            return

        # Проверяем не мой ли это ключ
        if file_name == my_file_name:
            await message.answer("Имя файла предназначено для моего ГОСПОДИНА если вы направили его в ответ, то на этом можно завершать обмен ключами, иначе измените имя файла если он должен содержать ваш ключ\n\nРАДИ ВСЕХ БОГОВ НЕ МЕНЯЙТЕ ИМЯ ФАЙЛА")
            # Определяем выходной файл
            file_path = os.path.join(TEMP_DIR, file_name)
            await bot.download(document, destination=file_path)
            
            result = subprocess.run(
                ['./gpg_2_script.sh', file_path],
                capture_output=True,
                text=True
            )
            return
        
        # Отправляем сообщение о начале обработки
        processing_msg = await message.answer("⏳ Файл получен. Начинаю обработку...")
        
        # Скачиваем файл
        file_path = os.path.join(TEMP_DIR, file_name)
        await bot.download(document, destination=file_path)
        
        await processing_msg.edit_text("✅ Файл скачан. Запускаю GPG скрипт...")
        
        # Запускаем GPG скрипт
        result_file = await process_gpg_file(file_path)
        
        if result_file and os.path.exists(result_file):
            # Отправляем результат
            await message.reply_document(
                document=types.FSInputFile(file_path),
                caption="✅ Результат обработки GPG"
            )
            
            # Удаляем временные файлы
            #os.remove(file_path)
            #os.remove(result_file)
            
            await processing_msg.delete()

            # Отправляем мой ключ
            
            const_file_path = os.path.join(CONST_DIR, my_file_name)
            await bot.send_document(
                chat_id=message.chat.id,
                document=types.FSInputFile(const_file_path),
                caption="Это файл с ключом моего ГОСПОДИНА ради всего святого подпишите его и отправьте обратно мне чтобы я добавил вашу подпись к ключу"
            )
        else:
            await processing_msg.edit_text(f"❌ Ошибка при обработке GPG файла {result_file}")
            
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.reply(f"❌ Произошла ошибка: {str(e)}")

# Обработчик файлов (если файл отправлен как фото или другой тип)
@dp.message(F.photo | F.video | F.audio | F.voice | F.video_note | F.sticker | F.animation)
async def handle_other_media(message: Message):
    await message.reply("❌ Пожалуйста, отправьте файл с расширением .asc как документ")

async def process_gpg_file(input_file: str) -> str:
    """
    Функция для обработки GPG файла.
    Здесь можно реализовать различные операции с GPG
    """
    try:
        # Определяем выходной файл
        input_path = Path(input_file)
        output_file = input_path.parent / f"decrypted_{input_path.stem}.txt"
        
        result = subprocess.run(
            ['./gpg_script.sh', input_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Если выходной файл создан, возвращаем его
            if output_file.exists():
                return str(output_file)
            else:
                # Если выходной файл не создан, создаем файл с результатом
                info_file = input_path.parent / f"gpg_info_{input_path.stem}.txt"
                with open(info_file, 'w') as f:
                    f.write(result.stdout)
                    if result.stderr:
                        f.write("\n\nSTDERR:\n")
                        f.write(result.stderr)
                return str(info_file)
        else:
            logging.error(f"GPG ошибка: {result.stderr}")
            return None
            
    except Exception as e:
        logging.error(f"Ошибка при выполнении GPG: {e}")
        return None

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())